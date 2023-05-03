#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import os
import pandas as pd
import mlflow
import json
import uuid
from azure.ai.ml import MLClient
from azure.cosmos import  CosmosClient
import azure.ai.ml._artifacts._artifact_utilities as artifact_utils
from utils.credential import get_credential, is_local
from utils.sql_connection import sqlalchemy_connection
from utils.config import ensure_path

# for this template, we load the models into an array - but you will likely only have 1
loaded_models = []
script_dir = os.path.dirname(__file__)
assets_dir = f"{script_dir}/../serve_assets"

def init(config):
    
    # set up SQL and cosmos connections
    credential = get_credential()
       
    global sql_connection
    sql_connection = sqlalchemy_connection(config)

    global cosmos_container
    if is_local() != True:
        uri = config["monitoring_store"]["uri"]
        client = CosmosClient(uri, credential=credential)
        database = client.get_database_client(config["monitoring_store"]["database_name"])
        cosmos_container = database.get_container_client(
            config["monitoring_store"]["container_name"]
        )
    
    # If running locally - pull model + datasets from local AML
    # If running in hosting - pull from shared registry
    if is_local():
        ml_client_registry = MLClient(credential=credential,
                        resource_group_name=config["aml"]["resource_group_name"],
                        subscription_id=config["subscription_id"],
                        workspace_name=config["aml"]["workspace_name"])
    else:
        ml_client_registry = MLClient(credential=credential,
                        registry_name=config["registry"]["name"],
                        registry_location=config["registry"]["location"])
    
    # loop the models in config and download them from the registry
    if "models" in config:
        for model in config["models"]:
            logging.info(f'Downloading model {model["name"]}, version {model["version"]}')

            # download the model, clearing out the old dir first
            download_path = f'{assets_dir}/models/{model["name"]}/{model["version"]}'
            ensure_path(download_path)

            ml_client_registry.models.download(
                name=model["name"], 
                version=model["version"], 
                download_path=download_path
            )
            
            loaded_models.append(mlflow.pyfunc.load_model(f'{download_path}/{model["name"]}/mlflow-model'))

    # loop the datasets in config and download them from the registry
    if "datasets" in config:
        for dataset in config["datasets"]:
            logging.info(f'Downloading dataset {dataset["name"]}, version {dataset["version"]}')

            # download the model, clearing out the old dir first
            download_path = f'{assets_dir}/datasets/{dataset["name"]}/{dataset["version"]}'
            ensure_path(download_path)

            ds = ml_client_registry.data.get(
                name=dataset["name"], 
                version=dataset["version"]
            )

            data = ml_client_registry.data.get(name=dataset["name"], version=dataset["version"])
            artifact_utils.download_artifact_from_aml_uri(
                uri = data.path, 
                destination = download_path,
                datastore_operation=ml_client_registry.datastores)


def run(config, user_inputs: dict = None):
    # TODO: Add code here that calls your model
    #       model_inputs is a dictionary containing any inputs that were passed to the model endpoint
    #       This function should return a dictionary containing the model results
    
    # get feature data
    query = """SELECT top 10 [csn]
        ,[date_of_birth]
        ,[horizon_datetime]
        FROM [dbo].[date_of_birth_v1]"""

    features = pd.read_sql(query, sql_connection)

    # run prediction
    outputs = loaded_models[0].predict(pd.DataFrame.from_dict(user_inputs))
    
    # create results dict
    results = {
        "id": str(uuid.uuid4()), 
        "user_inputs": user_inputs,
        "features": features.to_dict(),
        "outputs": dict(enumerate(outputs.flatten(), 1))
    }

    # log user_inputs, features and outputs to cosmos for accuracy monitoring
    # Note - json.loads / dumps because of some date serialisation errors with the cosmos SDK
    if is_local():
        logging.info("Skipping cosmos item creation due to no local access to prod cosmos")
    else:
        cosmos_container.create_item(json.loads(json.dumps(results, default=str)))

    # return model results
    return results
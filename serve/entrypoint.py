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
import pandas as pd
from azure.ai.ml import MLClient
from utils.sql_connection import sqlalchemy_connection
from utils.credential import get_credential

models = []

def init(config):
    logging.info("Loading models")

    credential = get_credential()
    
    # Get a handle to the registry
    ml_client_registry = MLClient(credential=credential,
                        registry_name=config["registry"]["name"],
                        registry_location=config["registry"]["location"])

    # loop the models in config and download them from the registry
    for model in config["models"]:
        model_from_registry = ml_client_registry.models.get(
            name=model["name"], version=model["version"]
        )
        model["registry_path"] = model_from_registry.path,
        models.append(model_from_registry)


def run(config, model_inputs: dict = None):
    # TODO: Add code here that calls your model
    #       model_inputs is a dictionary containing any inputs that were passed to the model endpoint
    #       This function should return a dictionary containing the model results
    
    connection = sqlalchemy_connection(config)

    query = """SELECT top 10 [csn]
        ,[date_of_birth]
        ,[horizon_datetime]
        FROM [dbo].[date_of_birth_v1]"""

    df = pd.read_sql(query, connection)
    model_results = df.to_json()

    logging.info("Model run completed")

    # return model results
    return model_results

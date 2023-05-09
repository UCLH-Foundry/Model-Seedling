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
from azure.ai.ml import MLClient
from utils.config import ensure_path
import azure.ai.ml._artifacts._artifact_utilities as artifact_utils


def download_models_defined_in_config(config: dict, directory:str, ml_client_registry: MLClient) -> list:

    model_details = []
    
    # loop the models in config and download them from the registry
    if "models" in config:
        for model in config["models"]:
            logging.info(f'Downloading model {model["name"]}, version {model["version"]}')

            # download the model, clearing out the old dir first
            download_path = f'{directory}/models/{model["name"]}/{model["version"]}'
            ensure_path(download_path)

            ml_client_registry.models.download(
                name=model["name"], 
                version=model["version"], 
                download_path=download_path
            )

            # add the downloaded path to the object
            model["download_path"] = download_path

            model_details.append(model)
    
    return model_details


def download_datasets_defined_in_config(config: dict, directory:str, ml_client_registry: MLClient) -> list:

    dataset_details = []

    # loop the datasets in config and download them from the registry
    if "datasets" in config:
        for dataset in config["datasets"]:
            logging.info(f'Downloading dataset {dataset["name"]}, version {dataset["version"]}')

            # download the model, clearing out the old dir first
            download_path = f'{directory}/datasets/{dataset["name"]}/{dataset["version"]}'
            ensure_path(download_path)

            data = ml_client_registry.data.get(name=dataset["name"], version=dataset["version"])
            artifact_utils.download_artifact_from_aml_uri(
                uri = data.path, 
                destination = download_path,
                datastore_operation=ml_client_registry.datastores)
            
            dataset["download_path"] = download_path
            dataset_details.append(dataset)
    
    return dataset_details

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

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Data
from utils.config import model_config
from utils.credential import get_credential
from utils.ml_client_registry import ml_client_registry


def register_datasets():
    
    config = model_config()
    credential = get_credential()
    
    # Get a handle to the AML workspace
    local_aml_client = ml_client_registry(config, True)
    
    # loop the config and push the datasets to the local AML registry
    for dataset in config["datasets"]:
        print(f'Registering dataset {dataset["name"]}...')

        # check if dataset with name and version is already there - we need to error out as the SDK just silently continues
        try:
            existing_dataset = local_aml_client.data.get(name=dataset["name"], version=dataset["version"])
            if existing_dataset is not None:
                print(f'Dataset {dataset["name"]} with version {dataset["version"]} is already registered. Please increment the version to register again. Skipping...')
                continue                
        except Exception:
            # This is 'expected'. The SDK doesn't have a `try_get` type method, so if we want to check whether the dataset exists already we need try + catch
            pass

        dataset_to_register = Data(
            path=f'{dataset["local_directory_path"]}/{dataset["file_name"]}',
            type=AssetTypes.URI_FILE,
            description=dataset["description"],
            name=dataset["name"],
            version=str(dataset["version"]),
        )
        local_aml_client.data.create_or_update(dataset_to_register)
        print(f'Registered dataset {dataset["name"]}')

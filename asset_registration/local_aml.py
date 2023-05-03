from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Data
from utils.config import model_config
from utils.credential import get_credential


def register_datasets():
    
    config = model_config()
    credential = get_credential()
    
    # Get a handle to the AML workspace
    local_aml_client = MLClient(credential=credential,
                        resource_group_name=config["aml"]["resource_group_name"],
                        subscription_id=config["subscription_id"],
                        workspace_name=config["aml"]["workspace_name"])
    
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
            pass

        dataset_to_register = Data(
            path=dataset["local_directory_path"],
            type=AssetTypes.URI_FOLDER,
            description=dataset["description"],
            name=dataset["name"],
            version=str(dataset["version"]),
        )
        local_aml_client.data.create_or_update(dataset_to_register)
        print(f'Registered dataset {dataset["name"]}')
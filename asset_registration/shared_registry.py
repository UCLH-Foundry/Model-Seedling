import os
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Data
from utils.config import model_config, ensure_path
from utils.credential import get_credential
from utils.ml_client_registry import ml_client_registry
from utils.download_assets import download_datasets_defined_in_config, download_models_defined_in_config

script_dir = os.path.dirname(__file__)
transfer_dir = f"{script_dir}/../transfer_assets"

def register_shared_assets():
    
    config = model_config()
    credential = get_credential()
    ensure_path(transfer_dir)

    # Get a handle to the AML workspace
    local_aml_client = ml_client_registry(config, True)
    
    # Get a handle to the registry
    registry_client = ml_client_registry(config, False)

    # download all the models locally
    downloaded_model_details = download_models_defined_in_config(config, transfer_dir, local_aml_client)

    # download all the datasets locally
    downloaded_dataset_details = download_datasets_defined_in_config(config, transfer_dir, local_aml_client)
    
    # upload the models to the shared registry
    for model in downloaded_model_details:
        print(f'Copying model {model["name"]}...')

        # check if model with name and version is already there - we need to let the user know we're skipping
        try:
            existing_model = registry_client.models.get(name=model["name"], version=model["version"])
            if existing_model is not None:
                print(f'Model {model["name"]} with version {model["version"]} is already registered. Please increment the version to register a new one. Skipping...')
                continue
        except Exception:
            pass

        # TODO revisit .share() when connectivity is fixed. For now, download and upload models
        # Share model. make sure the models have the same version in the local and global registries
        # local_aml_client.models.share(
        #     name=model["name"],
        #     version=model["version"],
        #     registry_name=config["registry"]["name"], 
        #     share_with_name=model["name"], 
        #     share_with_version=model["version"])

        registry_client.models.create_or_update(
            name=model["name"],
            version=str(model["version"]),
            description=model["description"],
            type=AssetTypes.ML_FLOW if model["is_mlflow"] else AssetTypes.CUSTOM,
            path=model["download_path"]
        )

        print(f'Copied model {model["name"]} with version {model["version"]} to shared registry.')
            
    # upload datasets to shared registry
    for dataset in downloaded_dataset_details:
        print(f'Registering dataset {dataset["name"]}...')

        # check if dataset with name and version is already there - we need to let the user know we're skipping
        try:
            existing_dataset = registry_client.data.get(name=dataset["name"], version=dataset["version"])
            if existing_dataset is not None:
                print(f'Dataset {dataset["name"]} with version {dataset["version"]} is already registered. Please increment the version to register again. Skipping...')
                continue                
        except Exception:
            pass

        dataset_to_register = Data(
            path=dataset["download_path"],
            type=AssetTypes.URI_FOLDER,
            description=dataset["description"],
            name=dataset["name"],
            version=str(dataset["version"]),
        )
        registry_client.data.create_or_update(dataset_to_register)

        print(f'Copied dataset {dataset["name"]} with version {dataset["version"]} to shared registry.')

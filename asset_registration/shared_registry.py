import os
from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Model, Data
from utils.config import model_config, ensure_path
from utils.credential import get_credential
import azure.ai.ml._artifacts._artifact_utilities as artifact_utils

script_dir = os.path.dirname(__file__)
transfer_dir = f"{script_dir}/../transfer_assets"

def register_shared_assets():
    
    config = model_config()
    credential = get_credential()
    ensure_path(transfer_dir)

    # Get a handle to the AML workspace
    local_aml_client = MLClient(credential=credential,
                        resource_group_name=config["aml"]["resource_group_name"],
                        subscription_id=config["subscription_id"],
                        workspace_name=config["aml"]["workspace_name"])
    
    # Get a handle to the registry
    ml_client_registry = MLClient(credential=credential,
                        registry_name=config["registry"]["name"],
                        registry_location=config["registry"]["location"])
    
    # loop the config and push the models to the registry
    if "models" in config:
        for model in config["models"]:
            print(f'Copying model {model["name"]}...')

            # check if model with name and version is already there - we need to let the user know we're skipping
            try:
                existing_model = ml_client_registry.models.get(name=model["name"], version=model["version"])
                if existing_model is not None:
                    print(f'Model {model["name"]} with version {model["version"]} is already registered. Please increment the version to register a new one. Skipping...')
                    continue
            except Exception:
                pass

            # Download and upload model: revisit .share when connectivity is fixed
            # Share model. make sure the models have the same version in the local and global registries
            local_aml_client.models.share(
                name=model["name"],
                version=model["version"],
                registry_name=config["registry"]["name"], 
                share_with_name=model["name"], 
                share_with_version=model["version"])

            download_path = ensure_path(f'{transfer_dir}/models/{model["name"]}')
            local_aml_client.models.download(
                name=model["name"], 
                version=model["version"], 
                download_path=download_path
            )

            ml_client_registry.models.create_or_update(
                name=model["name"],
                version=model["version"],
                type=AssetTypes.ML_FLOW if model["is_mlflow"] else AssetTypes.CUSTOM,
                path=download_path
            )

            print(f'Copied model {model["name"]} with version {model["version"]} to shared registry.')
            
    # Copy datasets to shared registry
    if "datasets" in config:
        for dataset in config["datasets"]:
            print(f'Registering dataset {dataset["name"]}...')

            # check if dataset with name and version is already there - we need to let the user know we're skipping
            try:
                existing_dataset = ml_client_registry.data.get(name=dataset["name"], version=dataset["version"])
                if existing_dataset is not None:
                    print(f'Dataset {dataset["name"]} with version {dataset["version"]} is already registered. Please increment the version to register again. Skipping...')
                    continue                
            except Exception:
                pass

            # Copy and upload dataset
            # TODO: revisit after fixing bug with connectivity between local AML -> Registry
            data = local_aml_client.data.get(name=dataset["name"], version=dataset["version"])
            download_path = ensure_path(f'{transfer_dir}/datasets/{dataset["name"]}')
            artifact_utils.download_artifact_from_aml_uri(
                uri = data.path, 
                destination = download_path,
                datastore_operation=local_aml_client.datastores)

            dataset_to_register = Data(
                path=download_path,
                type=AssetTypes.URI_FOLDER,
                description=dataset["description"],
                name=dataset["name"],
                version=str(dataset["version"]),
            )
            ml_client_registry.data.create_or_update(dataset_to_register)

            print(f'Copied dataset {dataset["name"]} with version {dataset["version"]} to shared registry.')

from azure.ai.ml import MLClient
from utils.load_model_config import model_config
from utils.credential import get_credential


def register_shared_assets():
    
    config = model_config()
    credential = get_credential()

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
    for model in config["models"]:
        print(f'Registering model {model["name"]}...')

        # check if model with name and version is already there - we need to let the user know we're skipping
        try:
            existing_model = ml_client_registry.models.get(name=model["name"], version=model["version"])
            if existing_model is not None:
                print(f'Model {model["name"]} with version {model["version"]} is already registered. Please increment the version to register a new one. Skipping...')
                continue
        except Exception:
            pass

        # Share model. make sure the models have the same version in the local and global registries
        local_aml_client.models.share(name=model["name"],
                        version=model["version"],
                        registry_name=config["registry"]["name"], 
                        share_with_name=model["name"], 
                        share_with_version=model["version"])

        print(f'Copied model {model["name"]} with version {model["version"]} to shared registry.')
        
    # Copy datasets to shared registry
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

        # Copy and share dataset
        data_in_workspace = local_aml_client.data.get(name=dataset["name"], version=dataset["version"])
        data_ready_to_copy = local_aml_client.data._prepare_to_copy(data_in_workspace)
        ml_client_registry.data.create_or_update(data_ready_to_copy).wait()

        print(f'Copied dataset {dataset["name"]} with version {dataset["version"]} to shared registry.')

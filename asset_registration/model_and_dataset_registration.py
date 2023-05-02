from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Model
from utils.load_model_config import model_config
from utils.credential import get_credential

# TODO: 
# - Register datasets
# - Copy model from AML registry

def register_assets():
    
    config = model_config()
    credential = get_credential()

    # Get a handle to the workspace
   # ml_client = MLClient.from_config(
   #     credential=credential,
   # )
    
    # Get a handle to the registry
    ml_client_registry = MLClient(credential=credential,
                        registry_name=config["registry"]["name"],
                        registry_location=config["registry"]["location"])
    
    # loop the config and push the models to the registry
    for model in config["models"]:
        print(f'Registering model {model["name"]}...')

        # check if model with name and version is already there - we need to error out as the SDK just silently continues
        try:
            existing_model = ml_client_registry.models.get(name=model["name"], version=model["version"])
            if existing_model is not None:
                print(f'Model {model["name"]} with version {model["version"]} is already registered. Please increment the version.')
                exit()
        except Exception:
            pass # No matching model found, can continue - SDK doesn't have a try_get method

        model = Model(
            path=model["local_file_path"],
            type=AssetTypes.MLFLOW_MODEL if model["is_mlflow"] else AssetTypes.CUSTOM,
            name=model["name"],
            version=str(model["version"]),
            description=model["description"]
        )
        ml_client_registry.models.create_or_update(model)


    # Share model. make sure the models have the same version in the local and global registries
   # ml_client.models.share(name=config["model_name"],
   #                        version=config["model_version"],
   #                        registry_name=config["registry_name"], 
   #                        share_with_name=config["model_name"], 
   #                        share_with_version=config["model_version"])
    
    # Copy and share dataset
   # data_in_workspace = ml_client.data.get(name=config["dataset_name"], 
   #                                        version=config["dataset_version"])
   # data_ready_to_copy = ml_client.data._prepare_to_copy(data_in_workspace)
   # ml_client_registry.data.create_or_update(data_ready_to_copy).wait()


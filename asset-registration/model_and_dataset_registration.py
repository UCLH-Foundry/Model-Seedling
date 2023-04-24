from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

import json

if __name__ == '__main__':
    with open("./config.json") as f:
        config = json.load(f)

    credential = DefaultAzureCredential()

    # Get a handle to the workspace
    ml_client = MLClient.from_config(
        credential=credential,
    )
    
    # Get a handle to the registry
    ml_client_registry = MLClient(credential=credential,
                        registry_name=config["registry_name"],
                        registry_location=config["registry_location"])

    # Share model. make sure the models have the same version in the local and global registries
    ml_client.models.share(name=config["model_name"], version=config["model_version"], registry_name=config["registry_name"], share_with_name=config["model_name"], share_with_version=config["model_version"])
    
    # Copy and share dataset
    data_in_workspace = ml_client.data.get(name=config["dataset_name"], version=config["dataset_version"])
    data_ready_to_copy = ml_client.data._prepare_to_copy(data_in_workspace)
    ml_client_registry.data.create_or_update(data_ready_to_copy).wait()

    
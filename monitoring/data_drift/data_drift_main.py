import argparse
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml import MLClient, Input
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import load_component
from azure.ai.ml.entities import Environment
from azure.ai.ml import Input
from azure.ai.ml import dsl, Input, Output
import json
import os

with open("./config.json") as f:
        config = json.load(f)

@dsl.pipeline(compute=config["compute_target"])
def data_drift_pipeline(
    reference_data_path,
    new_data_path,
    mlflow_uri,
    logger_connection_string,
    model_name,
    model_version,
):
    measure_data_drift_component = load_component(f"./data_drift/data_drift.yml")

    # using data_prep_function like a python call with its own inputs
    data_drift_job = measure_data_drift_component(reference_data_path=reference_data_path,
                                                new_data_path=new_data_path,
                                                mlflow_uri=mlflow_uri,
                                                logger_connection_string=logger_connection_string,
                                                model_name=model_name,
                                                model_version=model_version)
    

def main():
    

    input_folder = config["input_folder"]
    reference_file_name = config["reference_file_name"]
    new_file_name = config["new_file_name"]
    experiment_name = config["experiment_name"]
    compute_target = config["compute_target"]
    model_name = config["model_name"]
    model_version = config["model_version"]

    ml_client = MLClient(
         DefaultAzureCredential(),
         subscription_id=os.getenv("SUBSCRIPTION_ID"),
         resource_group_name=os.getenv("RESOURCE_GROUP"),
         workspace_name=os.getenv("AML_WORKSPACE_NAME"),
    )
    

    
    print(ml_client.compute.get(compute_target))

    DEFAULT_DOCKER_BASE_IMAGE = 'mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04'

    env_docker_image = Environment(
        image=DEFAULT_DOCKER_BASE_IMAGE,
        name="data-drift-env",
        conda_file="./data_drift/env.yml",    
        )

    pipeline_job_env = ml_client.environments.create_or_update(env_docker_image)


    data_store_prefix = "azureml://datastores/workspaceblobstore/paths"
    # Retrieve files from a remote location such as the Blob storage
    reference_data_path = Input(
        path=f"{data_store_prefix}/{input_folder}/{reference_file_name}", #this path needs to be adjusted to your datastore path
        type= "uri_file"
    )

    new_data_path = Input(
        path=f"{data_store_prefix}/{input_folder}/{new_file_name}", #this path needs to be adjusted to your datastore path
        type= "uri_file"
    )

    mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
    #measure_data_drift_component = load_component(f"data_drift.yml")

    pipeline_job = data_drift_pipeline(reference_data_path=reference_data_path,
                                                new_data_path=new_data_path,
                                                mlflow_uri=mlflow_tracking_uri,
                                                logger_connection_string=os.getenv("AZURE_LOG_HANDLER_CONNECTION_STRING"),
                                                model_name = model_name,
                                                model_version = model_version)
    
    pipeline_job.settings.default_compute=compute_target
    pipeline_job.settings.default_datastore="workspaceblobstore"

    pipeline_job = ml_client.jobs.create_or_update(
    pipeline_job, experiment_name=experiment_name
)

if __name__ == '__main__':
    main()

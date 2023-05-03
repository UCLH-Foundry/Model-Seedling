# Model and Dataset Registration

## Introduction

Each team developing a model works in isolation in their own TRE workspace, with their own AML instance. Once the team is happy with the model they've built and would like to progress the trained model from the TRE into a shared space that can be used in production, they will run a script that will create a copy of the model and dataset in a shared AML registry.
The shared registry will then be accessed from the production environment to pull the model and dataset into the workspace or for model deployment.

The AML registry is immutable and models can not be overwritten. Therefore, it would be the data scientists responsibility to create new version to each asset they would like to register.

## Setup
* Install the requirements
```
pip install -r dev_requirements.txt
```
* Make sure the following resources are available:
  * A model registered in the local workspace
  * A dataset registered as an AML dataset

## Running the Script

Before running the script, the data scientist will need to edit the `config.json` file to reflect the current workspace configuration (subscription ID, resource group, workspace name), the name and version of the model we would like to register, the name and version of the dataset we would like to register and the name and location of the registry.

Note that the AML registry won't allow asset overwrite, so the data scientist needs to make sure that the registry doesn't contain an asset with the same name and version.

After editing the `config.json` file, run the script to register the model and dataset.

## Downloading the model from the registry

In order to download the model for deployment, you would need to link to the AML registry and fetch the model from there. That could be done using the following piece of python code:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

registry_name = "<CHANGE_ME_REGISTRY_NAME>"
model_name = "<CHANGE_ME_MODEL_NAME>"
model_version = "<CHANGE_ME_MODEL_VERSION>"

credential = DefaultAzureCredential()
ml_client_registry = MLClient(credential=credential, registry_name=registry_name)

train_component_from_registry = ml_client_registry.models.download(
    name=model_name, version=model_version
)


```

That will create a local folder containing all of the model's artifacts. Similarly, to pull a dataset from the registry, run

```python

dataset_name = "<CHANGE_ME_DATASET_NAME>"
dataset_version = "<CHANGE_ME_DATASET_VERSION>"
dataset = ml_client_registry.data.download(name=dataset_name, version=dataset_version)
```

Or, if you would like to get a reference to the dataset and not download it (for example, if you would like the dataset to be used as an input for an AML job) run this command instead:

```python
dataset = ml_client_registry.data.get(name=dataset_name, version=dataset_version)
```

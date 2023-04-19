# Model and Dataset Registration

## Introduction

Each team developing a model works in isolation in their own TRE workspace, with their own AML instance. Once the team is happy with the model they've built and would like to progress the trained model from the TRE into a shared space that can be used in production, they will run a script that will create a copy of the model and dataset in a shared AML registry.
The shared registry will then be accessed from the production environment to pull the model and dataset into the workspace or for model deployment.

## Setup
* Install the requirements
```
pip install -r dev_requirements.txt
```
* Make sure the following resources are available:
  * An AML workspace
  * An [AML Registry](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-registries?view=azureml-api-2&tabs=studio)
  * A model registered in the local workspace
  * A dataset registered as an AML dataset

## Running the Script

Before running the script, the data scientist will need to edit the `config.json` file to reflect the current workspace configuration (subscription ID, resource group, workspace name), the name and version of the model we would like to register, the name and version of the dataset we would like to register and the name and location of the registry.

Note that the AML registry won't allow asset overwrite, so the data scientist needs to make sure that the registry doesn't contain an asset with the same name and version.

After editing the `config.json` file, run the script to register the model and dataset.


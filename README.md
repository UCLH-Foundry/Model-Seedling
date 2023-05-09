# Model Development and Endpoint Template

## Introduction 

This repo is a starting point for a new Data Science project. It provides a useful structure and development path to follow to provide some consistency to model building projects. 

The code here is yours to use and modify as best suits your work.

The steps in this repo will help you follow the full lifecycle from feature data to inferences being served in production
1. Create a new dataset from the feature store
1. Register that dataset in Azure Machine Learning (AML), within the TRE workspace you're working in
1. Run a training job in AML, registering a model at the end of it
1. Serve that model for inferencing locally, allowing you to test and iterate
1. Publish the models and datasets into a shared registry, where it can be referenced in Production.
1. Review and commit the code to Production, triggering an automated deployment into the FlowEHR infrastructure.

## Getting Started

If you're reading this, the repo should have been set up and made available to you in a TRE workspace. If not, please speak to your FlowEHR administrator to get your project added and created.

### Check model.yaml
All the code here relies on the `model.yaml` file in the root of the repo. Many of the values have been set already and can be left.

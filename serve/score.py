import os
import mlflow
import pandas as pd
import json
from azure.cosmos import  CosmosClient
import logging

MODEL_DIR = "credit_defaults_model"
DATABASE_NAME = "credit-default-db"
CONTAINER_NAME = "predictions"

def load_model():
    '''
    TODO: The function loads the MLFLOW model registered in AML. 
    Modify the function to reflect the location and type of the deployed model.
    AZUREML_MODEL_DIR is an environment variable created during deployment
    MODEL_DIR is the name of te directory where the model was logged
    '''
    model_path = os.path.join(os.environ["AZUREML_MODEL_DIR"], MODEL_DIR)
    model = mlflow.pyfunc.load_model(model_path)
    return model

def load_raw_data(raw_data):
    '''
    The function receives the raw data from the request and converts it 
    to a dataframe. The dataframe is then returned.
    TODO: the tempate expects the raw data to be in JSON format. 
    The structure of the JSON should be as follows:
    {
        "input_data": {
            "data": [
                [...],
                ...
            ],
            "columns": ["col1","col2",...,"col10"]
        }
    }
            
    '''
    raw_data = json.loads(raw_data)
    df = pd.DataFrame(raw_data["input_data"]["data"], columns=raw_data["input_data"]["columns"])
    return df

def log_records(df):
    '''
    The function logs the predictions to the Cosmos DB container.
    '''
    records = df.to_dict(orient='records')

    for i,record in enumerate(records):
        record['id'] = 'item{0}'.format(i+4)
        container.create_item(record)
    return records

def init():
    # Perform any initialization of the model
    
    global model
    global container

    logging.info("Model initialized")

    # Connect to the Cosmos DB container
    uri = "<COSMOSDB_URI>"
    cosmos_key = "<COSMOSDB_KEY>"
    client = CosmosClient(uri, credential=cosmos_key)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    model = load_model()
    return {"init": "DONE"}

def run(raw_data):
    # Calling the model and returning the predictions

    df = load_raw_data(raw_data)
    df['predictions'] = model.predict(raw_data["input_data"]["data"])

    records = log_records(df)
    return records


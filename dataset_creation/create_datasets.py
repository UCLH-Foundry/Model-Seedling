import os
import shutil
import pandas as pd
from utils.load_model_config import model_config
from utils.sql_connection import sqlalchemy_connection

script_dir = os.path.dirname(__file__)
assets_dir = f"{script_dir}/../local_assets/datasets"


def create_datasets():
    
    config = model_config()
    sql_connection = sqlalchemy_connection(config)

    # repeat / refactor / remove as needed
    # -----
    dataset_name = "my-dataset"
    dataset_path = f'{assets_dir}/{dataset_name}/'
    ensure_path(dataset_path)

    query = """SELECT top 10 [csn]
        ,[date_of_birth]
        ,[horizon_datetime]
        FROM [dbo].[date_of_birth_v1]"""

    data = pd.read_sql(query, sql_connection)
    data.to_csv(f'{dataset_path}/{dataset_name}.csv')
    print(f'Created {dataset_name} in {dataset_path}. Update your model.yaml as needed.')
    # -----


def ensure_path(dataset_path):
    if os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)
    os.makedirs(dataset_path)


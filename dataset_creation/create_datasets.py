import os
import pandas as pd
from utils.config import model_config, ensure_path
from utils.sql_connection import sqlalchemy_engine

script_dir = os.path.dirname(__file__)
assets_dir = f"{script_dir}/../local_assets/datasets"


def create_datasets():
    
    config = model_config()
    sql_connection = sqlalchemy_engine(config).connect()

    # repeat / refactor / remove as needed
    # -----
    dataset_name = "my-dataset"
    dataset_path = f'{assets_dir}/{dataset_name}/'
    ensure_path(dataset_path)

    query = """SELECT top 10 [csn]
        ,[date_of_birth]
        ,[horizon_datetime]
        FROM [dbo].[date_of_birth_v1]"""

    # TODO - with
    data = pd.read_sql(query, sql_connection)
    data.to_csv(f'{dataset_path}/{dataset_name}.csv')
    print(f'Created {dataset_name} in {dataset_path}. Update your model.yaml as needed.')
    # -----
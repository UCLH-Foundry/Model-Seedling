#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import pandas as pd
from sqlalchemy import text
from utils.config import model_config, ensure_path
from utils.sql_connection import sqlalchemy_engine

script_dir = os.path.dirname(__file__)
assets_dir = f"{script_dir}/../local_assets/datasets"


def create_datasets():
    """
    This method is called via `make create-local-datasets`
    Modify this method to query the source data, and save the results locally, ready to publish to AML
    """
    
    config = model_config()
    sql_engine = sqlalchemy_engine(config)

    # TODO: repeat / refactor / remove as needed
    # -----
    dataset_name = "_CHANGE_ME_"
    dataset_path = f'{assets_dir}/{dataset_name}/'
    ensure_path(dataset_path)

    # read the dataset query in
    with open(f"{script_dir}/dataset_query.sql", "r") as stream:
        query = stream.read()

    # execute the dataset query, and save the results as a csv
    with sql_engine.connect() as sql_connection:
        data = pd.read_sql(text(query), sql_connection)
        data.to_csv(f'{dataset_path}/{dataset_name}.csv')
        print(f'Created {dataset_name} in {dataset_path}. Update your model.yaml as needed.')
    # -----

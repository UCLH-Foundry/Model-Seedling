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
import logging
from fastapi import FastAPI, Request

from serve.serve import Serve
from .azure_logging import initialize_logging, disable_unwanted_loggers
from .about import generate_about_json
from utils.config import model_config
from utils.cosmos_container import cosmos_container
from utils.ml_client_registry import ml_client_registry
from utils.credential import is_local
from utils.sql_connection import sqlalchemy_engine
from utils.download_assets import download_models_defined_in_config, download_datasets_defined_in_config

logger = logging.getLogger(__name__)

# if we're running in app-dev, don't init, don't connect to data or models - just return the fake
is_app_dev = "ENVIRONMENT" in os.environ and os.environ["ENVIRONMENT"].lower() == "app-dev"

# get config from yaml
config = model_config()

# only load models when not in app dev
home_dir = os.path.expanduser('~')
loaded_model_details, loaded_dataset_details = [], []
registry, sql_engine, cosmos = None, None, None
if is_app_dev != True:
    # get cosmos container for prod hosting only 
    cosmos = cosmos_container(config) if is_local() != True else None

    # get AML registry client - depending on environment
    registry = ml_client_registry(config, is_local())

    # build sql connection
    sql_engine = sqlalchemy_engine(config)

    # download models and datasets
    loaded_model_details = download_models_defined_in_config(config, f'{home_dir}/serve-assets', registry)
    loaded_dataset_details = download_datasets_defined_in_config(config, f'{home_dir}/serve-assets', registry)

# create fastapi app
app = FastAPI()

# instantiate user serve code
serve = Serve(
    config=config,
    sql_engine=sql_engine, 
    cosmos_container=cosmos,
    model_details=loaded_model_details, 
    dataset_details=loaded_dataset_details
)


@app.on_event("startup")
async def initialize_logging_on_startup():
    initialize_logging(logging.INFO)
    disable_unwanted_loggers()


@app.get("/")
def root():
    logging.info("Root endpoint called")
    return generate_about_json(config)


@app.get("/run")
def run_get(req: Request):
    return run(req.query_params)


@app.post("/run")
def run_post(rawdata: dict = None):
    return run(rawdata)


def run(rawdata: dict = None):
    logging.info("Run endpoint called")
    if is_app_dev:
        return serve.run_fake(rawdata)
    else:
        return serve.run(rawdata)

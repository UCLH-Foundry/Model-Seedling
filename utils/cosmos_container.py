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

from .credential import get_credential
from .credential import is_local
from azure.cosmos import CosmosClient

def cosmos_container(config):

    credential = get_credential
    uri = config["monitoring_store"]["uri"]
    client = CosmosClient(uri, credential=credential)
    database = client.get_database_client(config["monitoring_store"]["database_name"])
    
    return database.get_container_client(
        config["monitoring_store"]["container_name"]
    )

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
from azure.ai.ml import MLClient


def ml_client_registry(config, local_aml) -> MLClient:
    credential = get_credential()

    if local_aml:
        return MLClient(credential=credential,
                        resource_group_name=config["aml"]["resource_group_name"],
                        subscription_id=config["subscription_id"],
                        workspace_name=config["aml"]["workspace_name"])
    else:
        return MLClient(credential=credential,
                        registry_name=config["registry"]["name"],
                        registry_location=config["registry"]["location"])

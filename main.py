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

import uvicorn
from serve.internal import api
from asset_registration.shared_registry import register_shared_assets
from asset_registration.local_aml import register_datasets
from dataset_creation.create_datasets import create_datasets


if __name__ == "__main__":
    uvicorn.run(api.app, port=5000)

def make_create_datasets():
    create_datasets()

def make_register_datasets_in_aml():
    register_datasets()

def make_register_assets():
    register_shared_assets()

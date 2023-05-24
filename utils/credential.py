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
from azure.identity import DefaultAzureCredential


def is_local():
    return os.environ.get("ENVIRONMENT") is None


def get_credential():
    # if running code from the repo in the TRE, we need to exclude MSI else the identity of the VM is picked up first
    credential = DefaultAzureCredential(exclude_managed_identity_credential=is_local())
    return credential

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

import struct
import os
from typing import Any
import pyodbc
import sqlalchemy
from .credential import get_credential
from .credential import is_local


def get_connection_string(model_config):
    driver = "{ODBC Driver 18 for SQL Server}"
    server = model_config["feature_store"]["server"]
    database = model_config["feature_store"]["database"]
    msi = "" if is_local() else "Authentication=ActiveDirectoryMsi;"
    cs = f'Driver={driver};Server=tcp:{server},1433;Database={database};{msi}Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    return cs


def get_db_aad_token(model_config) -> bytes:
     
    tenant_id = model_config["aad_tenant_id"]
    credential = get_credential()
    databaseToken = credential.get_token("https://database.windows.net/", tenant_id=tenant_id)

    tokenb = bytes(databaseToken[0], "UTF-16 LE")
    token_struct = struct.pack("=i", len(tokenb)) + tokenb
    return token_struct

    
def pyodbc_connection(model_config) -> Any:
    """
    ODBC cursor for running queries against the MSSQL feature store.

    Documentation: https://github.com/mkleehammer/pyodbc/wiki
    """

    cs = get_connection_string(model_config)

    if is_local():
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        token_struct = get_db_aad_token(model_config)
        return pyodbc.connect(cs, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    else:
        return pyodbc.connect(cs) 

def sqlalchemy_connection(model_config) -> Any:
    """
    SQLAlchemy connection for running queries against the MSSQL feature store.
    """
    cs = get_connection_string(model_config)

    if is_local():
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        token_struct = get_db_aad_token(model_config)
        return sqlalchemy.create_engine(
            f"mssql+pyodbc:///?odbc_connect={cs}",
            connect_args={"attrs_before": {SQL_COPT_SS_ACCESS_TOKEN: token_struct}},
        ).connect()
    else:
        return sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={cs}").connect()

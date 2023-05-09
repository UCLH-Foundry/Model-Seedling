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
import json
import uuid
import mlflow
from sqlalchemy import Engine, text
from azure.cosmos import ContainerProxy


class Serve(object):

    def __init__(self,
            config: dict = None,
            sql_engine: Engine = None, 
            cosmos_container: ContainerProxy = None, 
            model_details = [], 
            dataset_details = []):
        """
        This method will get called once, at startup
        """

        self.config = config
        self.sql_engine = sql_engine
        self.cosmos_container = cosmos_container
        self.model_details = model_details
        self.dataset_details = dataset_details

        print("Models Loaded:", self.model_details)
        print("Datasets Loaded:", self.dataset_details)

        # TODO: Add any custom run-once logic here

        if model_details and len(model_details) > 0:
            self.my_model = mlflow.pyfunc.load_model(f'{self.model_details[0]["local_path"]}/{self.model_details[0]["name"]}/mlflow-model')
        
        # load the sql, ready to call for inferencing
        script_dir = os.path.dirname(__file__)
        with open(f"{script_dir}/feature_inference_query.sql", "r") as stream:
            self.feature_query = stream.read()

    def run(self, user_inputs: dict = None):
        """
        Accepts input from the user and returns a model prediction
        model_inputs is a dictionary containing any inputs that were passed to the model endpoint
        """

        # TODO: Validate the user input

        # get feature data
        with self.sql_engine.connect() as connection:
            # params are defined in the SQL query using :param_name, and passed in as a dictionary to read_sql()
            features = pd.read_sql(text(self.feature_query), connection, params={"csn": user_inputs["csn"]})
    
        # run prediction
        outputs = self.my_model.predict(features)
        
        # create results dict
        results = {
            "id": str(uuid.uuid4()), 
            "user_inputs": user_inputs,
            "features": features.to_dict(),
            "outputs": dict(enumerate(outputs.flatten(), 1)) # will have to modify this depending on the model output
        }

        # log user_inputs, features and outputs to cosmos for accuracy monitoring
        # Note - json.loads / dumps because of some date serialisation errors with the cosmos SDK
        if self.cosmos_container:
            self.cosmos_container.create_item(json.loads(json.dumps(results, default=str)))

        # return model results
        return results

    def run_fake(self, user_inputs: dict = None):
        """
        Use this method to return a sample payload in the app-dev environment.
        This will help app developers build against your model endpoint
        """

        return {
            "id": str(uuid.uuid4()), 
            "user_inputs": user_inputs,
            "features": {"feature1": "value1", "feature2": "value2"},
            "outputs": ["Shape", "Of", "Expected", "Predictions"]
        }

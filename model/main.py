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

from azure.ai.ml import command, Input, Output, dsl
from azure.ai.ml.entities import Environment
from utils.config import model_config
from utils.ml_client_registry import ml_client_registry
import os

def run_pipeline():

    config = model_config()
    script_dir = os.path.dirname(__file__)
    compute_instance = f'cp-{config["aml"]["aml_suffix"]}'

    ml_client = ml_client_registry(config, True)

    # get a reference to the dataset
    los_data = ml_client.data.get(name=config["datasets"][0]["name"], version=config["datasets"][0]["version"])

    # the AML 'environment' (conda + docker config) that runs the job
    pipeline_job_env = Environment(
        name = "Default Training Environment",
        description="TRE AML Training Environment",
        tags = {"a_tag": "can_go_here"},
        conda_file=f'{script_dir}/environment.yml',
        # the below docker image is available by default in the AML container registry, deployed via the TRE
        image = f'acrsvc{config["aml"]["aml_suffix"]}.azurecr.io/aml-tre-nexus-image' 
    )

    # now register the environment
    ml_client.environments.create_or_update(environment=pipeline_job_env)

    # in aml this is called a component but here called a command
    # the strings below are placeholders and the 'command' then substitutes in the actual args
    # which will come later
    # inputs include data and a name for the model
    # outputs include just a folder of stuff
    train_model_comp = command(
        name="_CHANGE_ME_",
        display_name="training model",
        description="_CHANGE_ME_",
        inputs={
            "train_data": Input(type="uri_file"),
            "registered_model_name": Input(type="string")
        },
        outputs = {
            "model": Output(type="uri_folder", mode="rw_mount")
        },
        code=f'{script_dir}/src',
        # see below: all the cli args are those specified in train.py
        command="""python train.py \
                    --train_data=${{inputs.train_data}} \
                    --registered_model_name=${{inputs.registered_model_name}} \
                    --model=${{outputs.model}}""",
        # environment from the object specified above
        environment=f"{pipeline_job_env.name}:{pipeline_job_env.version}"
    )

    # this decorator sets stuff up
    # using the train_model_comp 'command' that we set up before
    @dsl.pipeline(
        compute=compute_instance,
        description="End-to-End pipeline"
    )
    def train_a_model(pipeline_data, pipeline_model_name):
        train_job = train_model_comp(
            # could also put a data extract step 
            # so that the sql query is run on AML
            # but the authentication could be a problem /  as could tracking versions etc
            # could by the preprocess.py here
            train_data = pipeline_data,
            registered_model_name=pipeline_model_name
        )

    # now call the function to make this concrete with the placeholders
    # input is from aml, and passing the details neeed to make this work
    # and matches the 'input' defined above
    pipeline = train_a_model(
        pipeline_data=Input(type="uri_file", path=los_data.path),
        pipeline_model_name="_CHANGE_ME_")

    # GO GO GO!
    ml_client.jobs.create_or_update(pipeline, experiment_name="_CHANGE_ME_")

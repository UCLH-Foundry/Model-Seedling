from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential
from azure.ai.ml import MLClient, command, Input, Output, dsl
from azure.ai.ml.entities import Environment, Data
from azure.ai.ml.constants import AssetTypes
from utils.config import model_config
from utils.credential import get_credential
from utils.ml_client_registry import ml_client_registry
import os

# TODO: refactor. lots.
def run_pipeline():

    config = model_config()
    credential = get_credential()
    script_dir = os.path.dirname(__file__)
    compute_instance = f'cp-{config["aml"]["aml_suffix"]}'

    print(compute_instance)
    exit()

    ml_client = ml_client_registry(congig, True)

    # get a reference to the dataset
    los_data = ml_client.data.get(name=config["datasets"][0]["name"], version=config["datasets"][0]["version"])

    # the environment that runs the job
    # could abstract this out; the image below is an AML image on the local docker hub
    # will use the environment we specify to do the work
    # can see in the web interface under environments>custom (not curated)
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

    # in aml this 'thing' is called a component but here called a command
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
    # train_job is like a little make fle
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
    
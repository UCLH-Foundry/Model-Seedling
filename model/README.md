# AML Model Deployment Template

The following files are intended to provide a template within which a data science user can place their model script
for training within AML.

## Target User

The intended end-user profile for this code is someone who may be competent with pandas/scikit-learn,
but may not be comfortable modifying code outside of this framework.

We have taken the boilerplate AML code and abstracted this away into discrete non-user files:
* `main.py` = the user runs this when they are ready, but no code is modified here.
* `config.json` = the AML config file
* `src/aml_train` = this takes the user's model.py script and integrates with other AML code.

The user will be instructed on how to modify, as required, the following files:
* `src/model.py` = a dedicated file into which the user puts their model training script - exactly as they might run it on their own device.
* `user.json` = the user's config file for various parameters like cpu-instance name, experiment-name, etc
* `conda.yml` = the config file for the AML conda environment

Currently, this code only runs using a pre-stored `.csv` file. As we progress with SQL/EMAP work in the TRE, the scope of the following two files should become clearer (user-modifiable vs non-user-modifiable):
* `src/data_prep` = current script for loading in the .csv data
* `src/data_versioning` = empty placeholder file, representing a potential script that pulls in EMAP data as a 'version'

In its current format, the main.py script <i>should</i> run to completion, training an XGBoost classifier on the `spotlightearly.csv` data file.
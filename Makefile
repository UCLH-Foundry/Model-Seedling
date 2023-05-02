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
# limitations under the License.
.PHONY: help

SHELL:=/bin/bash
MAKEFILE_FULLPATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_FULLPATH))

target_title = @echo -e "🌱$(1)..."

help: ## Show this help
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%s\033[0m|%s\n", $$1, $$2}' \
        | column -t -s '|'
	@echo

deploy: build ## Deploy this app
	$(call target_title, "Deploying") \
	&& . ${MAKEFILE_DIR}/.scripts/load_env.sh \
	&& ${MAKEFILE_DIR}/.scripts/deploy.sh

build:  ## Build the docker image
	$(call target_title, "Building") \
	&& . ${MAKEFILE_DIR}/.scripts/load_env.sh \
	&& ${MAKEFILE_DIR}/.scripts/build.sh

# Steps - TBC:

# - init the repo [make init]

# - create CSV [make create-local-dataset]

# - register dataset in AML [make register-dataset]

# (have a dataset, in AML)
# - train model [make train-model-in-aml]
#   - register model at end of training

# (have a registered model in AML)
# - test model as local API [make serve-local]
#   - if is_local, pull model + dataset from local AML registry
#   - else: pull from shared registry

# (ready to publish + serve model)
# - algo steward runs make publish-assets [make publish-assets-in-registry]
# - commit code + PR to prod branch
# deployment magic happens


# Data Science Steps
init:
	$(call target_title, "Installing Requirements") \
	&& pip install -r requirements.txt

create-local-datasets:
	$(call target_title, "Creating dataset") \
	&& python3 -c 'import main; main.make_create_datasets()'

register-datasets-in-aml:
	$(call target_title, "Registering datasets in AML") \
	&& python3 -c 'import main; main.make_register_datasets_in_aml()'

train-model-in-aml:
# TODO


serve-local:  ## Serve the model locally
	$(call target_title, "Serving locally") \
	&& python3 main.py

publish-assets-in-registry:  ## Push the model and dataset to the shared registry
	$(call target_title, "Pushing Models and Datasets to registry") \
	&& python3 -c 'import main; main.make_register_assets()'

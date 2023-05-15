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


# Automation make targets -----------------------------------------------------

deploy: build ## Deploy this app
	$(call target_title, "Deploying") \
	&& . ${MAKEFILE_DIR}/.scripts/load_env.sh \
	&& ${MAKEFILE_DIR}/.scripts/deploy.sh

build:  ## Build the docker image
	$(call target_title, "Building") \
	&& . ${MAKEFILE_DIR}/.scripts/load_env.sh \
	&& ${MAKEFILE_DIR}/.scripts/build.sh


# Data science workflow steps -------------------------------------------------

init:  ## Download all dependencies
	$(call target_title, "Installing Requirements") \
	&& pip install -r requirements.txt

create-local-datasets:  ## Run scripts to create local datasets for training
	$(call target_title, "Creating dataset") \
	&& python3 -c 'import make_targets; make_targets.make_create_datasets()'

register-datasets-in-aml:  ## Register local datasets in AML
	$(call target_title, "Registering datasets in AML") \
	&& python3 -c 'import make_targets; make_targets.make_register_datasets_in_aml()'

train-model-in-aml:  ## Run model training in AML and register a model
	$(call target_title, "Submitting training job to AML") \
	&& python3 -c 'import make_targets; make_targets.train_model_in_aml()'

serve-local:  ## Serve the model endpoint locally for testing
	$(call target_title, "Serving locally") \
	&& python3 main.py

serve-local-app-dev:  ## Serve the model endpoint locally to check what an app developer will see in app-dev
	$(call target_title, "Serving locally in app-dev mode") \
	&& ENVIRONMENT=app-dev python3 main.py

publish-assets-in-registry:  ## Push the model and dataset to the shared registry
	$(call target_title, "Pushing Models and Datasets to registry") \
	&& python3 -c 'import make_targets; make_targets.make_register_assets()'

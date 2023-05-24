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

import argparse
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
import polars as pl
import os
import mlflow
from model import train_model


# =================================================
"""
Logging the model training process
"""

# Start Logging
mlflow.start_run()

# enable autologging - this is specific to scikit-learn models only
mlflow.sklearn.autolog()

os.makedirs("./outputs", exist_ok=True)


# =================================================
"""
Running the training script in AML

The main() function will load your training / testing data, and then run
your model-training script. 
"""


def main():

    # TODO: The code below is an illustration to use a basis for your work. 
    # Change the training code below as needed.

    # input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data", type=str, help="path to train data")
    parser.add_argument("--registered_model_name", type=str, help="model name")
    parser.add_argument("--model", type=str, help="path to model file")
    args = parser.parse_args()

    # Locate the training/testing data
    df = (pl.read_csv(args.train_data, null_values=["NULL"])
            .select(["csn", "systolic", "diastolic", "hr", "rr", "temp", "o2_sat", "age", "hrs_to_discharge"])
            .with_columns(
                (pl.col("hrs_to_discharge") < 24).alias("discharge_24_hours")
            )).drop(["hrs_to_discharge"])

    
    df_train = df.sample(fraction=0.75, seed=42)
    df_test = df.join(df_train, on="csn", how="anti")

    X_train = df_train.drop(["csn", "discharge_24_hours"])
    y_train = df_train.drop_in_place("discharge_24_hours")

    X_test = df_test.drop(["csn", "discharge_24_hours"])
    y_test = df_test.drop_in_place("discharge_24_hours")

    model, train_metrics, test_metrics = train_model(X_train, y_train, X_test, y_test)

    # Log the output from the training process
    mlflow.log_metrics(train_metrics)
    mlflow.log_metrics(test_metrics)

    # Registering the model to the workspace
    mlflow.sklearn.log_model(
        sk_model=model,
        registered_model_name=args.registered_model_name,
        artifact_path=args.registered_model_name,
    )

    # Saving the model to a file
    mlflow.sklearn.save_model(
        sk_model=model,
        path=os.path.join(args.model, "trained_model"),
    )

    # Stop Logging
    mlflow.end_run()


if __name__ == "__main__":
    main()

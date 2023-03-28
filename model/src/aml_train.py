import argparse
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, f1_score
import os
import pandas as pd
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

    def select_first_file(path):
        """
        This function provides the path to the training or testing file.
        NOTE: it assumes there is only one file in the folder (e.g., train.csv)

        Args:
            path (str): path to the parent directory
        Returns:
            str: path to the training/testing file
        """
        files = os.listdir(path)
        return os.path.join(path, files[0])

    # input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data", type=str, help="path to train data")
    parser.add_argument("--test_data", type=str, help="path to test data")
    parser.add_argument("--registered_model_name", type=str, help="model name")
    parser.add_argument("--model", type=str, help="path to model file")
    args = parser.parse_args()

    # Locate the training/testing data csvs and load into a DataFrame
    train_df = pd.read_csv(select_first_file(args.train_data))
    test_df = pd.read_csv(select_first_file(args.test_data))

    # Convert the training and testing data into numpy arrays
    y_train = train_df["dead7"].values
    X_train = train_df.drop('dead7', axis=1).values
    y_test = test_df['dead7'].values
    X_test = test_df.drop('dead7', axis=1).values

    print('Beginning training...')
    model, train_metrics, test_metrics = train_model(X_train, y_train, X_test, y_test)

    # Log the output from the training process
    mlflow.log_metrics(train_metrics)
    mlflow.log_metrics(test_metrics)

    # Registering the model to the workspace
    print("Registering the model via MLFlow")
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

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

from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, f1_score


# =================================================
"""
INTRODUCTION
This file serves as your model training script for AML.

The function takes numpy arrays as its input - these can be training and testing arrays,
or just the training arrays.

The function name MUST be left as train_model, and should NOT be changed.
"""


def train_model(X_train, y_train, X_test=None, y_test=None):
    """
    YOUR TRAINING SCRIPT GOES HERE

    Args:
        X_train (numpy array): training data as a numpy array
        y_train (numpy array): training labels as a numpy array
        X_test (numpy array) [OPTIONAL]: testing data as a numpy array
        y_test (numpy array) [OPTIONAL]: testing data as a numpy array
    Returns:
        model: fitted model
        train_metrics: training metrics
        test_metrics: testing metrics
    """

    # Example script

    # Define the model
    model = XGBClassifier()

    # Fit the model
    model.fit(X_train, y_train)

    # Evaluate the model
    y_train_pred = model.predict(X_train)
    if X_test is not None:
        y_test_pred = model.predict(X_test)

    train_metrics = {'train_accuracy': accuracy_score(y_train, y_train_pred),
                     'train_roc_auc_score': roc_auc_score(y_train, y_train_pred),
                     'train_f1_score': f1_score(y_train, y_train_pred)}

    if X_test is not None:
        test_metrics = {'test_accuracy': accuracy_score(y_test, y_test_pred),
                        'test_roc_auc_score': roc_auc_score(y_test, y_test_pred),
                        'test_f1_score': f1_score(y_test, y_test_pred)}
    else:
        test_metrics = {}

    """
    Your function MUST return, in the following order:
    1) A working model
    2) A dictionary of your desired training metrics
    3) A dictionary of your desired testing metrics
    """

    return model, train_metrics, test_metrics

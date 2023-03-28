import argparse
import mlflow
import os
import pandas as pd
from sklearn.compose import  make_column_selector as selector
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score,roc_auc_score



def main(args):
    logger = logging.getLogger(__name__)
    logger.addHandler(AzureLogHandler(connection_string=args.logger_connection_string))

    mlflow.set_tracking_uri(args.mlflow_uri)
    mlflow.start_run()
    run_id = mlflow.active_run().info.run_id

    inference_data_path = args.inference_data_path
    groundtruth_data_path = args.groundtruth_data_path
    

    inf_df = pd.read_csv(inference_data_path)
    ground_df = pd.read_csv(groundtruth_data_path)
    df = pd.merge(inf_df,ground_df,on=args.index_name,how='outer')
    metrics = {'accuracy':accuracy_score(df['ground_truth'],df['pred']),
               'f1_score':f1_score(df['ground_truth'],df['pred']),
               'precision':precision_score(df['ground_truth'],df['pred']),
               'recall':recall_score(df['ground_truth'],df['pred']),
               'roc':roc_auc_score(df['ground_truth'],df['pred']),}
    
    mlflow.log_metrics(metrics)
    metrics['run_id'] = run_id

    properties = {'custom_dimensions': metrics}
    logger.warning('model_performance', extra=properties)

   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inference_data_path', type=str,default='/Users/ayabellicha/Documents/model-monitoring-design/tabular-data/reference_data.csv')
    parser.add_argument('--groundtruth_data_path', type=str,default='/Users/ayabellicha/Documents/model-monitoring-design/tabular-data/new_data.csv')
    parser.add_argument('--index_name', type=str,default="Unnamed: 0")
    parser.add_argument('--mlflow_uri', type=str,default='.')
    parser.add_argument('--logger_connection_string', type=str,default='.')
    args = parser.parse_args()

    main(args)
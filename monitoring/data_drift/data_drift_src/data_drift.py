import argparse
import mlflow
import os
import pandas as pd
from sklearn.compose import  make_column_selector as selector
import numpy as np
from matplotlib import pyplot as plt
from alibi_detect.cd import TabularDrift
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
import seaborn as sns

def kde_plot(x_ref, x_new, title):
    plt.figure()
    dist_plot = sns.kdeplot(x_ref, shade=True, color='blue', label='reference')
    sns.kdeplot(x_new, shade=True, color='red', label='new')
    dist_plot.set_title(title)
    fig = dist_plot.get_figure()
    return fig

def cat_bar_plot(reference_df,new_df,col,drift_detected):
    ref_counts = reference_df[col].value_counts(normalize=True).reset_index()
    ref_counts['source']='reference data'

    new_counts = new_df[col].value_counts(normalize=True).reset_index()
    new_counts['source']='new data'

    counts_df = pd.concat([ref_counts,new_counts])
    plt.figure()
    fig = sns.barplot(x=col,y='index',hue='source',data=counts_df)
    fig.set_title(f'{col}: drift detected: {bool(drift_detected)}')
    fig = fig.get_figure()

    return fig



def main(args):
    logger = logging.getLogger(__name__)
    logger.addHandler(AzureLogHandler(connection_string=args.logger_connection_string))

    mlflow.set_tracking_uri(args.mlflow_uri)
    mlflow.start_run()
    run_id = mlflow.active_run().info.run_id

    reference_data_path = args.reference_data_path
    new_data_path = args.new_data_path
    #output_path = args.output_path

    reference_df = pd.read_csv(reference_data_path)
    new_df = pd.read_csv(new_data_path)

    # identify categorical columns
    categorical_columns_selector = selector(dtype_include=object)
    categorical_columns = categorical_columns_selector(reference_df)
    categories_per_feature = {list(reference_df.columns).index(i):None for i in categorical_columns}

    cd = TabularDrift(reference_df.values, p_val=.05,categories_per_feature=categories_per_feature)
    preds = cd.predict(new_df[reference_df.columns].values, drift_type='batch')
    fpreds = cd.predict(new_df[reference_df.columns].values, drift_type='feature')

    properties = {'custom_dimensions': {'is_drift': int(max(fpreds['data']['is_drift']))
               ,'run_id':run_id }}
    logger.warning('data_drift_total', extra=properties)

    p_values = {reference_df.columns[i]:fpreds['data']['p_val'][i] for i in range(len(reference_df.columns))}

    p_values = pd.DataFrame([p_values]).T
    
    #fig = plt.figure(figsize=(50,50))
    plt.figure()
    heatplot = sns.heatmap(p_values,annot=True,cmap=['red','blue'],center=0.05)
    heatplot.figure.suptitle('P vals summary')
    fig = heatplot.get_figure()
    mlflow.log_figure(fig, f'pvalues_summary.png')


    for id,col in enumerate(reference_df.columns):
        properties = {'custom_dimensions': {'feature_name': col, 'is_drift': int(fpreds['data']['is_drift'][id]),
                  'distances': str(fpreds['data']['distance'][id]),
                  'p_values': str(fpreds['data']['p_val'][id]),
                  'run_id': run_id
                }}
        
        mlflow.log_metrics({f'{col}_drift': int(fpreds['data']['is_drift'][id]),
                            f'{col}_distance': fpreds['data']['distance'][id],
                            f'{col}_p_value': fpreds['data']['p_val'][id]})
    
        if id in categories_per_feature.keys():
            fig = cat_bar_plot(reference_df,new_df,col,int(fpreds['data']['is_drift'][id]))
            mlflow.log_figure(fig, f'{col}_frequency.png')

            most_frequent_category_new = new_df[col].value_counts(normalize=True)
            properties['custom_dimensions']['most_common_category_new'] = most_frequent_category_new.index[0]
            properties['custom_dimensions']['most_common_category_freq_new'] = str(most_frequent_category_new[0])

            most_frequent_category_ref = reference_df[col].value_counts(normalize=True)
            properties['custom_dimensions']['most_common_category_ref'] = most_frequent_category_ref.index[0]
            properties['custom_dimensions']['most_common_category_freq_ref'] = str(most_frequent_category_ref[0])
        else:
            drift_detected = bool(fpreds['data']['is_drift'][id])
            title = f'{col}: drift: {drift_detected}'
            plt.figure()
            fig = kde_plot(reference_df[col], new_df[col], title)
            mlflow.log_figure(fig, f'{col}_kde.png')
            properties['custom_dimensions']['mean_new'] = new_df[col].mean()
            properties['custom_dimensions']['mean_ref'] = reference_df[col].mean()

        logger.warning('data_drift_features', extra=properties)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference_data_path', type=str,default='/Users/ayabellicha/Documents/model-monitoring-design/tabular-data/reference_data.csv')
    parser.add_argument('--new_data_path', type=str,default='/Users/ayabellicha/Documents/model-monitoring-design/tabular-data/new_data.csv')
    parser.add_argument('--mlflow_uri', type=str,default='.')
    parser.add_argument('--logger_connection_string', type=str,default='.')
    args = parser.parse_args()

    main(args)
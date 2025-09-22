import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## Counts the number of entries in the 'system' DataFrame that match 'gold' entries for a given cluster.
# Loops through rows in the 'gold' DataFrame and counts the number of matching entries in the 'system' DataFrame.
# @param system: The 'system' DataFrame.
# @param gold: The 'gold' DataFrame.
# @param cluster_id: The column name for the cluster identifier.
# @param entries: The column name for entries in the cluster.
# @param number: The cluster number to match.
# @param system_row: The row from the 'system' DataFrame.
# @return: The count of matching entries, the length of 'system' entries, and the length of 'gold' entries.
#
def count_same(system, gold, cluster_id, entries, number, system_row):
    counter = 0
    for gold_index, gold_row in gold.iterrows():
        if number == gold_row[cluster_id]:
            length_gold_entries = gold_row['number_gold_entries']
            if isinstance(system_row[entries], list):
                length_system_entries = len(system_row[entries])                         
                for x in range(0, length_system_entries):
                    for y in range(0, length_gold_entries):
                        if int(system_row[entries][x].strip("'")) == gold_row[entries][y]:
                            counter = counter + 1
            else:
                length_system_entries = 1
                for y in range(0, length_gold_entries):
                    if int(system_row[entries]) == gold_row[entries][y]:
                        counter = counter + 1
    return counter, length_system_entries, length_gold_entries

## Performs F1 analysis comparing clusters in the 'system' DataFrame to those in the 'gold' DataFrame.
# Loops through rows in the 'system' DataFrame and calculates precision, recall, and F1 measure for each cluster.
# Returns a DataFrame with cluster-level analysis results sorted by F1 measure.
# @param system: The 'system' DataFrame.
# @param gold: The 'gold' DataFrame.
# @param cluster_id: The column name for the cluster identifier.
# @param entries: The column name for entries in the cluster.
# @return: A DataFrame containing cluster-level analysis results.
#
def f1_analysis(system, gold, cluster_id, entries):
    df = pd.DataFrame(columns=[cluster_id, 'count_same', 'number_system_entries', 'number_gold_entries'])
    index = 0
    for system_index, system_row in system.iterrows():
        if isinstance(system_row[cluster_id], list):
            for i in range(0, len(system_row[cluster_id])):
                number = int(system_row[cluster_id][i].strip("'"))
                counter, number_system_entries, number_gold_entries = count_same(system, gold, cluster_id, entries, number, system_row)
                new_row = {cluster_id: number, 'count_same': counter, 'number_system_entries': number_system_entries, 'number_gold_entries': number_gold_entries}
                df.loc[index] = new_row
                index = index + 1
        else:
            number = int(system_row[cluster_id])
            counter, number_system_entries, number_gold_entries = count_same(system, gold, cluster_id, entries, number, system_row)
            new_row = {cluster_id: number, 'count_same': counter, 'number_system_entries': number_system_entries, 'number_gold_entries': number_gold_entries}
            df.loc[index] = new_row
            index = index + 1
    df['precision'] = df.apply(precision, axis=1)
    df['recall'] = df.apply(recall, axis=1)
    df['f1_measure'] = df.apply(f1_measure, axis=1)
    df = df.sort_values(by='f1_measure', ascending=False).reset_index(drop=True)
    return df

## Calculates precision for a row.
# @param row: The row containing 'count_same' and 'number_system_entries'.
# @return: The precision calculated as 'count_same' / 'number_system_entries'.
#
def precision(row):
    return row['count_same'] / row['number_system_entries']

## Calculates recall for a row.
# @param row: The row containing 'count_same' and 'number_gold_entries'.
# @return: The recall calculated as 'count_same' / 'number_gold_entries'.
 #   
def recall(row):
    return row['count_same'] / row['number_gold_entries']

## Calculates the F1 measure based on precision and recall.
# Computes the F1 measure as 2 * (precision * recall) / (precision + recall).
# If both precision and recall are zero, the F1 measure is set to zero to avoid division by zero.
# @param row: A DataFrame row containing 'precision' and 'recall' values.
# @return: The F1 measure for the given row.
#
def f1_measure(row):
    if row['precision'] + row['recall'] == 0:
        return 0
    else:
        return 2*row['precision']*row['recall'] / (row['precision'] + row['recall'])

## Calculates the weighted median of a list of values based on corresponding weights.
# Sorts the values and weights together, calculates the total weight, and finds the midpoint.
# Iterates through the sorted data and determines the value where cumulative weight crosses the midpoint.
# @param values: List of values to calculate the weighted median from.
# @param weights: List of weights corresponding to the values.
# @return: The weighted median of the values.
#
def weighted_median(values, weights):
    sorted_data = sorted(zip(values, weights))
    values, weights = zip(*sorted_data)
    total_weight = sum(weights)
    midpoint = total_weight / 2
    cumulative_weight = 0
    for value, weight in zip(values, weights):
        cumulative_weight += weight
        if cumulative_weight >= midpoint:
            return value

## Calculates the length of a text.
# @param text: The text for which the length is to be calculated.
# @return: The length of the text.
#
def calculate_length(text):
    return len(text)
        
## Calculates the F1 measure based on precision and recall.
# @param df: Golden patstat.
# @param dc: System cluster.
# @return: A DataFrame containing cluster-level analysis results.
#
def f1_measure_top100(df,dc):
    #Create the golden cluster.
    dg = df.groupby('cluster_id')['npl_publn_id'].apply(list).reset_index()
    
    #Calculate the length (number of elements) for each list of 'npl_publn_id' and store it in a new column 'number_gold_entries'.
    dg['number_gold_entries'] = dg['npl_publn_id'].apply(calculate_length)
    
    #Calculate precision, recall, and F1 measure for each cluster using the f1_analysis function.
    #Then, select the top 100 rows based on the 'f1_measure' column.
    df1_measure = f1_analysis(dc, dg, 'cluster_id', 'npl_publn_id')
    df1_measure = df1_measure.head(100)
    
    #save table as excel
    #table_precision_recall_f1_analysis = df1_measure[['cluster_id', 'precision', 'recall', 'f1_measure']].copy()
    #table_precision_recall_f1_analysis.to_excel('table_precision-recall-f1_analysis.xlsx', sheet_name='Sheet1', index=False)
    
    print('done f1 analysis')
    return df1_measure

## Generates the output table and a scatter plot for precision, recall, and F1 measure.
# The function calculates various weighted and non-weighted averages for precision, recall, and F1 measure.
# It also creates a table and a scatter plot to visualize the F1 scores for clusters.
# @param df1_measure: A DataFrame containing F1 analysis results for clusters.
#
def output(df1_measure):
    output = pd.DataFrame(columns=['','precision', 'recall', 'f1_measure'])
    
    # Calculate weighted and non-weighted averages for precision, recall, and F1 measure
    weighted_average_precision = np.average(df1_measure['precision'], weights=df1_measure['count_same'])
    weighted_median_precision = weighted_median(df1_measure['precision'], df1_measure['count_same'])
    weighted_average_recall = np.average(df1_measure['recall'], weights=df1_measure['count_same'])
    weighted_median_recall = weighted_median(df1_measure['recall'], df1_measure['count_same'])
    weighted_average_f1_measure = np.average(df1_measure['f1_measure'], weights=df1_measure['count_same'])
    weighted_median_f1_measure = weighted_median(df1_measure['f1_measure'], df1_measure['count_same'])
    non_weighted_average_precision = df1_measure['precision'].mean()
    non_weighted_median_precision = df1_measure['precision'].median()
    non_weighted_average_recall = df1_measure['recall'].mean()
    non_weighted_median_recall = df1_measure['recall'].median()
    non_weighted_average_f1_measure = df1_measure['f1_measure'].mean()
    non_weighted_median_f1_measure = df1_measure['f1_measure'].median()
    
    # Create rows for different average calculations
    non_weighted_avg_row = pd.DataFrame({'': 'non_weighted_avg', 'precision': [non_weighted_average_precision], 'recall': [non_weighted_average_recall], 'f1_measure': [non_weighted_average_f1_measure]})
    weighted_avg_row = pd.DataFrame({'': 'weighted_avg', 'precision': [weighted_average_precision], 'recall': [weighted_average_recall], 'f1_measure': [weighted_average_f1_measure]})
    non_weighted_med_row = pd.DataFrame({'': 'non_weighted_med', 'precision': [non_weighted_median_precision], 'recall': [non_weighted_median_recall], 'f1_measure': [non_weighted_median_f1_measure]})
    weighted_med_row = pd.DataFrame({'': 'weighted_med', 'precision': [weighted_median_precision], 'recall': [weighted_median_recall], 'f1_measure': [weighted_median_f1_measure]})
    
    output = pd.concat([output, non_weighted_avg_row, weighted_avg_row, non_weighted_med_row, weighted_med_row], ignore_index=True)
    
    # Print the output table
    print(output.to_string(index=False))
    
    # Create a scatter plot to visualize F1 scores for clusters
    fig, ax = plt.subplots()
    
    ax.scatter(df1_measure.index, df1_measure['f1_measure'], marker='o', color='b')
    ax.set_ylim(0, 1.05)
    
    ax.set_xlabel('Clusters')
    ax.set_ylabel('F1_score')
    ax.set_title('Plot for Precision-Recall-F1 scores')
    
    # Save the plot as a PDF
    #plt.savefig('plot_for_precision-recall-f1_scores.pdf', format='pdf')
    
    plt.show()
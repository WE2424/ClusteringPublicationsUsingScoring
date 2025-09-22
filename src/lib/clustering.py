import pandas as pd

class Clustering:
    def __init__(self, jaccard_threshold_words, col_list, threshold, a_list):      
        self.jaccard_threshold_words = jaccard_threshold_words
        self.col_list = col_list
        self.threshold = threshold
        self.a_list = a_list

    ## Clusters data in the 'df' DataFrame.
    # Initializes an empty 'dc' DataFrame with the same columns as 'df'.
    # Loops through rows in 'df' and compares them with existing clusters in 'dc' using 'sim_check_row'.
    # If similarity counter is less than the threshold, adds a new cluster using 'add_new_cluster'.
    # Finally, sorts the 'dc' DataFrame based on 'npl_publn_id'.
    # @param df: The DataFrame to be clustered.
    # @return: The 'dc' DataFrame after clustering.
    #
    def cluster_data(self, df):
        dc = pd.DataFrame(columns=df.columns) 
        counter = 0
        for df_index, df_row in df.iterrows():
            for dc_index, dc_row in dc.iterrows():
                counter = 0
                counter = self.sim_check_row(dc_row, df_row, counter)
                if counter >= self.threshold:
                    dc = self.add_to_cluster(dc, dc_row, df_row, dc_index)
                    break
            if counter < self.threshold:
                dc = self.add_new_cluster(dc, df_row)
            dc = self.sort_dataframe(dc, 'npl_publn_id')
        print('done clustering')
        return dc

    ## Computes the Jaccard index for two strings based on word-level similarity.
    # @param str1: The first string.
    # @param str2: The second string.
    # @return: The Jaccard index, a measure of word-level similarity between the two strings.
    #
    def jaccard_index_words(self, str1, str2):
        words1 = set(str1.split())  # Split the first string into words and create a set
        words2 = set(str2.split())  # Split the second string into words and create a set
        intersection = len(words1.intersection(words2))  # Calculate the number of common words
        union = len(words1) + len(words2) - intersection  # Calculate the total number of unique words
        return intersection / union if union != 0 else 0.0  # Compute the Jaccard index

    ## Checks the similarity of two strings and increments a counter if they are similar.
    # The similarity is measured using the Jaccard index (word-level) or numeric equality.
    # @param str1: The first string.
    # @param str2: The second string.
    # @param a_col: The value to increment the counter by if the strings are similar.
    # @param counter: The current counter value.
    # @return: The updated counter value.
    #
    def sim_check_value(self, str1, str2, a_col, counter):
        if str1 is not None and str2 is not None:
            if str1.isnumeric() and str2.isnumeric():
                if str1 == str2:
                    counter = counter + a_col
            else:
                if self.jaccard_index_words(str1, str2) >= self.jaccard_threshold_words:
                    counter = counter + a_col
        return counter

    ## Checks the similarity between two cells in a given column and increments a counter if they are similar.
    # The similarity is measured based on the `sim_check_value` function.
    # @param col: The column for which to compare the cells.
    # @param a_col: The value to increment the counter by if the cells are similar.
    # @param dc_row: The row from the 'dc' DataFrame.
    # @param df_row: The row from the 'df' DataFrame.
    # @param counter: The current counter value.
    # @return: The updated counter value.
    #
    def sim_check_cell(self, col, a_col, dc_row, df_row, counter):
        if counter < self.threshold:
            if isinstance(dc_row[col], list):
                for i in range(0, len(dc_row[col])):
                    if isinstance(df_row[col], list):
                        for j in range(0, len(df_row[col])):
                            counter = self.sim_check_value(dc_row[col][i], df_row[col][j], a_col, counter)
                    else:
                        counter = self.sim_check_value(dc_row[col][i], df_row[col], a_col, counter)
            else:
                if isinstance(df_row[col], list):
                    for j in range(0, len(df_row[col])):
                        counter = self.sim_check_value(dc_row[col], df_row[col][j], a_col, counter)
                else:
                    counter = self.sim_check_value(dc_row[col], df_row[col], a_col, counter)
        return counter

    ## Checks the similarity of all cells in two rows using the `sim_check_cell` function.
    # @param dc_row: The row from the 'dc' DataFrame.
    # @param df_row: The row from the 'df' DataFrame.
    # @param counter: The current counter value.
    # @return: The updated counter value.
    #
    def sim_check_row(self, dc_row, df_row, counter):
        for i in range(0, len(self.col_list)):
            counter = self.sim_check_cell(self.col_list[i], self.a_list[i], dc_row, df_row, counter)
        return counter

    ## Adds a value to a cluster (column) in the 'dc' DataFrame.
    # @param column: The column (cluster) in which to add the value.
    # @param dc: The 'dc' DataFrame.
    # @param vdc: The current value in the 'dc' DataFrame.
    # @param vdf: The value to be added.
    # @param dc_index: The index in the 'dc' DataFrame.
    # @return: The updated 'dc' DataFrame.
    #
    def add_to_cluster_value(self, column, dc, vdc, vdf, dc_index):
        if str(vdf) != 'None' and str(vdc) != 'None' and vdc is not None and vdf is not None:
            b = 0
            if isinstance(vdc, list):
                for i in range(0, len(vdc)):
                    if str(vdc[i]) == str(vdf):
                        b = 1
                        break
                if b == 0:
                    dc.loc[dc_index, column].append(str(vdf))
            elif b == 0 and str(vdc) != str(vdf):
                dc.at[dc_index, column] = [str(vdc), str(vdf)]
            else:
                dc.loc[dc_index, column] = str(vdf)
        return dc

    ## Adds values to clusters in the 'dc' DataFrame based on similarity with values in the 'df' DataFrame.
    # Loops through columns in the 'dc' DataFrame and adds values to the corresponding clusters using `add_to_cluster_value`.
    # @param dc: The 'dc' DataFrame.
    # @param dc_row: The row from the 'dc' DataFrame.
    # @param df_row: The row from the 'df' DataFrame.
    # @param dc_index: The index in the 'dc' DataFrame.
    # @return: The updated 'dc' DataFrame.
    #
    def add_to_cluster(self, dc, dc_row, df_row, dc_index):
        for column in dc.columns:
            if isinstance(df_row[column], list):
                for j in range(0, len(df_row[column])):
                    dc = self.add_to_cluster_value(column, dc, dc_row[column], df_row[column][j], dc_index) 
            else:
                dc = self.add_to_cluster_value(column, dc, dc_row[column], df_row[column], dc_index)
        return dc

    ## Adds a new cluster to the 'dc' DataFrame by concatenating the 'df' row as a new row.
    # @param dc: The 'dc' DataFrame.
    # @param df_row: The row from the 'df' DataFrame.
    # @return: The updated 'dc' DataFrame.
    #
    def add_new_cluster(self, dc, df_row):
        dc = pd.concat([dc, df_row.to_frame().T], ignore_index=True)
        return dc

    ## Sorts a DataFrame based on the length of values in a specified column.
    # Calculates the length of values in the specified column, adds this as a new temporary column,
    # sorts the DataFrame based on this temporary column, and then removes the temporary column.
    # @param df: The DataFrame to be sorted.
    # @param col: The column used for sorting.
    # @return: The sorted DataFrame.
    #
    def sort_dataframe(self, df, col):
        df_sorted = df.assign(Column1_Length=df[col].astype(str).str.len()).sort_values(by='Column1_Length', ascending=False).drop('Column1_Length', axis=1)
        return df_sorted
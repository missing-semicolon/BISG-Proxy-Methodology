"""
This script creates the master surname list from the census surname file,
including the proportions of individuals by race and ethnicity by surname.
"""

import os
import numpy as np
import pandas as pd


def create(in_csv):
    census_surnames_lower_file = '../input_files/created_python/census_surnames_lower.pkl'
    if not os.path.isfile(census_surnames_lower_file):

        raw_in = pd.read_csv(in_csv)
        print("Loaded DataFrame {} of length {:,} and columns: {}".format(in_csv, raw_in.shape[0], list(raw_in.columns)))

        output = raw_in.copy()

        print(raw_in['name'].iloc[:5])
        output['name'] = output['name'].apply(lambda x: str(x).lower())
        print(output['name'].iloc[:5])

        class_vars = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic']

        print(output[class_vars].iloc[:5])

        def convert_to_decimal(x):
            try:
                return float(x) / 100
            except:
                return None

        output[class_vars] = output[class_vars].applymap(convert_to_decimal)

        def replace_missing_pcts(x):
            count_miss = np.sum(x.isnull())
            remaining = 1 - np.sum(x)
            replacement = remaining / count_miss
            x[x.isnull()] = replacement
            return x

        print(output[class_vars].iloc[151669, :])
        output[class_vars] = output[class_vars].apply(replace_missing_pcts, axis=1)
        print(output[class_vars].iloc[151669, :])

        output.to_pickle(census_surnames_lower_file)
    else:
        print("Loading {}".format(census_surnames_lower_file))
        output = pd.read_pickle(census_surnames_lower_file)

    return output

"""
This script uses the base information from the census flat files for block group, tract, and ZIP code and allocates "Some Other Race"
to each group in proportion.  It creates three files (one each for block group, tract, and ZIP code) containing the geography-only
proxy as well as the proportion of population for a given race and ethnicity residing in a given geographic area, which is 
used to build the BISG proxy.
"""


import os
import numpy as np
import pandas as pd


def create(indir, outdir):
    geo_files = ['blkgrp', 'tract', 'zip']
    file_stem = '_over18_race_dec10'
    for geo_file in geo_files:
        geo_file = geo_file + file_stem
        if not os.path.isfile(os.path.join(outdir, geo_file + '.pkl')):
            print("Creating {}...".format(geo_file))
            raw_in = pd.read_stata(os.path.join(indir, geo_file + '.dta'))

            # Step 1: From the SF1, retain population contiguous U.S., Alaska,
            # and Hawaii in order to ensure consistency with the population
            # covered by the census surname list.
            print("Initial Number of State_FIPS10 == 72: {}".format(
                (raw_in['State_FIPS10'] == '72').sum()))
            output = raw_in[raw_in['State_FIPS10'] != "72"]
            print("Updated Number of State_FIPS10 == 72: {}".format(
                (output['State_FIPS10'] == '72').sum()))

            if geo_file == 'zip' + file_stem:
                print('Initial Number of ZCTA5s beginning with "006","007","008","009": {}'.format(
                    (raw_in['State_FIPS10'].apply(lambda x: x[:3] in ["006", "007", "008", "009"])).sum()))
                output = raw_in[(raw_in['ZCTA5'].apply(
                    lambda x: x[:3] not in ["006", "007", "008", "009"]))]
                print('Updated Number of ZCTA5s beginning with "006","007","008","009": {}'.format(
                    (output['State_FIPS10'].apply(lambda x: x[:3] in ["006", "007", "008", "009"])).sum()))

            # Step 2: Address "Other" category from 2010 Census; what is done
            # here follows Word(2008).

            for var in ['NH_White', 'NH_Black', 'NH_AIAN', 'NH_API']:
                output[var + "_alone"] = output[var +
                                                "_alone"] + output[var + "_Other"]

            # Census breaks out Asian and PI separately; since we consider them
            # as one, we correct for this.
            output['NH_API_alone'] = output['NH_API_alone'] + \
                output['NH_Asian_HPI'] + output['NH_Asian_HPI_Other']

            # Replace multiracial total to account for the fact that we have
            # suppressed the Other category.
            output['NH_Mult_Total'] = output['NH_Mult_Total'] - (np.sum(
                output[['NH_White_Other', 'NH_Black_Other', 'NH_AIAN_Other', 'NH_Asian_HPI', 'NH_API_Other', 'NH_Asian_HPI_Other']], axis=1))

            # Verify the steps above by confirming that the Total Population
            # still matches.
            assert np.array_equal(output['Total_Pop'].values,
                                  np.sum(output[['NH_White_alone', 'NH_Black_alone', 'NH_API_alone', 'NH_AIAN_alone', 'NH_Mult_Total', 'NH_Other_alone', 'Hispanic_Total']], axis=1).values)

            # Step 3: Proportionally redistribute Non-Hispanic Other population
            # to remaining Non-Hispanic groups within each block.
            for var in ['NH_White_alone', 'NH_Black_alone', 'NH_AIAN_alone', 'NH_API_alone', 'NH_Mult_Total']:
                output[var] = output[var] + (output[var] / (output['Total_Pop'] - np.sum(
                    output[['Hispanic_Total', 'NH_Other_alone']], axis=1))) * output['NH_Other_alone']
                output[output['Total_Pop'] == 0][var] = 0
                output[output['Non_Hispanic_Total'] == output['NH_Other_alone']][
                    var] = output['NH_Other_alone'] / 5

            # Verify the steps above by confirming that all sole-ethnicities sum to the total population.
            assert np.array_equal(output['Total_Pop'].values,
                                  round(np.sum(output[['NH_White_alone', 'NH_Black_alone', 'NH_AIAN_alone', 'NH_API_alone', 'NH_Mult_Total', 'Hispanic_Total']], axis=1)).values)

        else:
            print("{}.pkl already exists.".format(
                os.path.join(outdir, geo_file)))

"""
This script uses the base information from the census flat files for block group, tract, and ZIP code and allocates "Some Other Race"
to each group in proportion.  It creates three files (one each for block group, tract, and ZIP code) containing the geography-only
proxy as well as the proportion of population for a given race and ethnicity residing in a given geographic area, which is 
used to build the BISG proxy.
"""


import os
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
            # and Hawaii in order to ensure consistency with the population covered by the census surname list.
            print("Initial Number of State_FIPS10 == 72: {}".format((raw_in['State_FIPS10'] == '72').sum()))
            output = raw_in[raw_in['State_FIPS10'] != "72"]
            print("Updated Number of State_FIPS10 == 72: {}".format((output['State_FIPS10'] == '72').sum()))

            
            if geo_file == 'zip' + file_stem:
                print('Initial Number of ZCTA5s beginning with "006","007","008","009": {}'.format((raw_in['State_FIPS10'].apply(lambda x: x[:3] in ["006", "007", "008", "009"])).sum()))
                output = raw_in[(raw_in['ZCTA5'].apply(lambda x: x[:3] not in ["006", "007", "008", "009"]))]
                print('Updated Number of ZCTA5s beginning with "006","007","008","009": {}'.format((output['State_FIPS10'].apply(lambda x: x[:3] in ["006", "007", "008", "009"])).sum()))

            # Step 2: Address "Other" category from 2010 Census; what is done here follows Word(2008).

            for var in []


        else:
            print("{}.pkl already exists.".format(os.path.join(outdir, geo_file)))

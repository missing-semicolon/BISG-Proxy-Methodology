"""This program is called from an external script and merges the name probabilities
and census geography data to generate the Bayesian updated probability.

Input arguments:

matchvars() - unique record identifier
maindir() - output directory
readdir() - directory containing individual or application data
readfile() - individual or application data file
geodir() - input directory that contains geocoded data
geofile() - institution specific geocoded data
inst_name() - string that is use to create file name for final output dataset
censusdir() - directory containing prepared input census geography and surname data
geo_ind_name() - string that identifies the name of the geographic indicator in the loan or individual level analysis data (the program will change the name of the fips variable in the geocoded data to match this in order to merge)
geo_switch() - string that identifies level of geography used taking the following values: blkgrp, tract, or zip (same values as used in geo creator)"""

import os
import pandas as pd


def merge_geofile_and_readfile_by_matchvars(geofile, readfile, matchvars=[]):
    geofile = pd.read_pickle(geofile)
    readfile = pd.read_pickle(readfile)

    if not matchvars:
        geofile = geofile.reset_index()
        readfile = readfile.reset_index()
        matchvars = ['index']

    return geofile.merge(readfile, how='inner', on=matchvars)


def load_census_file(censusdir, geo_switch, geo_ind_name):
    df = pd.read_pickle(os.path.join(censusdir, geo_switch + '_over18_race_dec10.pkl'))
    df = df.rename(columns={'GeoInd': geo_ind_name})
    return df


def load_orig_data(orig_file_path, matchvars=[]):
    df = pd.read_pickle(orig_file_path)
    # for var in matchvars:
    #     if var == 'index':

    return df


def load_surname_data(surname_file_path, matchvars=[]):
    df = pd.read_pickle(surname_file_path)
    for var in matchvars:
        try:
            assert var in list(df)
        except:
            print("The match variable {} is not present in the surname data.".format(var))

    return df


def create(output, orig_dir, orig_file, surname_dir, surname_file, censusdir, geo_switch,
           orig_surname_match=[], surname_census_match=[]):

    print("\n\n\n")
    print("************************************************")
    print("************    Creating BISG Data    **********")
    print("************************************************\n\n\n")

    geo_dict = {'blkgrp': 'GEOID10_BlkGrp',
                'tract': 'GEOID10_Tract',
                'zip': 'ZCTA5'}

    for geo_type in geo_switch:

        print("Merging {} with {}".format(geo_type, surname_file))

        geo_ind_name = geo_dict[geo_type]

        orig_data = load_orig_data(os.path.join(orig_dir, orig_file), matchvars=orig_surname_match)
        print("Loaded Original Data {} (Shape: {})".format(orig_file, orig_data.shape))

        surname_data = load_surname_data(os.path.join(surname_dir, surname_file), surname_census_match)
        print("Loaded Surname Data {} (Shape: {})".format(surname_file, surname_data.shape))

        merged_surname_data = orig_data.merge(surname_data, how='left', left_index=True, right_index=True)
        print("Created Merged Surname Data (Shape: {})".format(merged_surname_data.shape))

        census_df = load_census_file(censusdir, geo_switch=geo_type, geo_ind_name=geo_dict[geo_type])
        print("Loaded Census Data {} (Shape: {})".format(geo_type, census_df.shape))

        combined_proxy_and_census = census_df.merge(merged_surname_data, how='inner', left_on=geo_ind_name, right_on=surname_census_match)
        print("Merged Census Data with Surname Data by {} (Shape: {})".format(geo_ind_name, combined_proxy_and_census.shape))

        combined_proxy_and_census.to_pickle('tmp.pkl')  # UAT

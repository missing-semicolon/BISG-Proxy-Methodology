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
import numpy as np


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


def rename_post_pr_vars(df):
    to_rename = [var for var in list(df) if var.startswith('post_pr')]
    prefix_dict = {var: 'name_pr_' + var[8:] for var in to_rename}
    df = df.rename(columns=prefix_dict)
    df = df.rename(columns={'name_pr_2prace': 'name_pr_mult_other'})
    return df


def create_BISG(df):
    race_list = ['white', 'black', 'aian', 'api', 'mult_other', 'hispanic']

    for race in race_list:
        df['u_' + race] = df['name_pr_' + race] * df['here_given_' + race]

    df['u_sum'] = np.sum(df[[var for var in list(df) if var.startswith('u_')]], axis=1)

    for race in race_list:
        df['pr_' + race] = df['u_' + race] / df['u_sum']

    drop_list = [var for var in list(df) if var.startswith('u_') or var.startswith('here_')]
    df = df.drop(drop_list, axis=1)

    df['prtotal'] = np.sum(df[[var for var in list(df) if var.startswith('pr_')]], axis=1)

    return df


def check_BISG(df):
    print("Beginning BISG Sanity Checks...")
    race_list = ['white', 'black', 'aian', 'api', 'mult_other', 'hispanic']

    for race in race_list:
        print("All probabilities should be between 0 and 1.")
        if not df.ix[df['prtotal'] < 0.99].empty:
            df = df.ix[df['prtotal'] < 0.99, 'pr_' + race] = np.NaN

        print("---Checking name_pr_{}".format(race))
        assert (((df['name_pr_' + race] >= 0.0) & (df['name_pr_' + race] <= 1.0)) | (df['name_pr_' + race].isnull())).all()

        print("---Checking geo_pr_{}".format(race))
        assert (((df['geo_pr_' + race] >= 0.0) & (df['geo_pr_' + race] <= 1.0)) | (df['geo_pr_' + race].isnull())).all()

        print("---Checking pr_{}\n".format(race))
        assert (((df['pr_' + race] >= 0.0) & (df['pr_' + race] <= 1.0)) | (df['pr_' + race].isnull())).all()

    print("Race probabilities should sum to at least 1.")
    for prob_type in ['name_', 'geo_', '']:
        print("---Checking sum of probabilities for {}.".format(prob_type + 'pr'))
        check_type = np.sum(df[[prob_type + 'pr_' + var for var in race_list]], axis=1)
        assert ((check_type == 0) | ((check_type >= 0.99) & (check_type <= 1.01))).all()

    print("All QC Checks Passed!")

    return df


def save_data_to_output(output, orig_data, ds):
    orig_data = orig_data.split('.')[0]
    ds.to_pickle(os.path.join(output, orig_data + '_BISG.pkl'))


def create(output, orig_dir, orig_file, surname_dir, surname_file, censusdir, geo_switch,
           orig_surname_match=[], surname_census_match=[]):

    print("\n\n\n")
    print("************************************************")
    print("************    Creating BISG Data    **********")
    print("************************************************")
    print("\n\n\n")

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

        combined_proxy_and_census = rename_post_pr_vars(combined_proxy_and_census)

        create_BISG_data = create_BISG(combined_proxy_and_census)

        final_BISG_data = check_BISG(create_BISG_data)

        save_data_to_output(output, orig_file, final_BISG_data)

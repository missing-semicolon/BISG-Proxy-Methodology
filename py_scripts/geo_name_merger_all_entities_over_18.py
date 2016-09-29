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


def create(output, readdir, readfile, geodir, geofile, inst_name, censusdir, geo_switch, matchvars=[]):

    geo_dict = {'blkgrp': 'GEOID10_BlkGrp',
                'tract': 'GEOID10_Tract',
                'zip': 'ZCTA5'}

    for geo_type in geo_switch:

        print("Merging {}".format(geo_type))

        geo_ind_name = geo_dict[geo_type]

        proxied_data = merge_geofile_and_readfile_by_matchvars(geofile=os.path.join(geodir, geofile),
                                                               readfile=os.path.join(readdir, readfile), matchvars=matchvars)

        # proxied_data = pd.read_pickle(os.path.join(geodir, geofile))


        census_df = load_census_file(censusdir, geo_switch=geo_type, geo_ind_name=geo_dict[geo_type])


        combined_proxy_and_census = census_df.merge(proxied_data, how='inner', left_on=geo_ind_name, right_on='zip_sample').reset_index()

        # combined_proxy_and_census = combined_proxy_and_census.merge()

        print(combined_proxy_and_census.head())

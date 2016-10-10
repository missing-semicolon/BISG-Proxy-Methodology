"""
This Python script executes a series of Python scripts and subroutines that prepare input public use census geography and surname data and constructs the surname-only, georgraphy-only, and BISG proxies for race and ethnicity.

This file is set up to execute the proxy building code sequence on a set of ficitious data constructed by create_test_data.py from the publicly available census surname list and geography data. It is provided to illustrate how the main.py is set up to run the proxy building code.
"""
import os

import surname_creation_lower
import create_attr_over18_all_geo_entities
import surname_parser
import geo_name_merger_all_entities_over_18


def main():

    # Identify the input directory that contains the individual or application level data containing name and geocodes.

    source_dir = "../input_files"

    # Identify the output directory for processing.
    out_dir = "../test_output"

    # Identify the location of the prepared input census files.
    census_data = "../input_files/created_python"

    geo_dir = "../input_files/created_python"

    # Run the script that prepares the analysis version of the census surname list, including the proportions of individuals by race and ethnicities by surname.
    census_surnames_lower = surname_creation_lower.create("../input_files/app_c.csv")

    create_attr_over18_all_geo_entities.create(source_dir, census_data)

    # Read in the file that defines the program "name_parse" that contains the name standardization routines and merges surname probabilities
    # from the census surname list.
    # See script for details on arguments that need to be supplied to the program.
    surname_probabilities = surname_parser.parse(matchvars=[], app_lname='name1', coapp_lname='name2', output=out_dir, readdir='../test_output', readfile='fictitious_sample_data.pkl', censusdir=census_data)

    geo_name_merger_all_entities_over_18.create(output=out_dir, orig_dir=out_dir, orig_file='fictitious_sample_data.pkl', surname_dir=out_dir, surname_file='proxy_name.pkl', orig_surname_match=[], surname_census_match=['zip_sample'], censusdir=census_data, geo_switch=['zip'])


if __name__ == '__main__':
    main()

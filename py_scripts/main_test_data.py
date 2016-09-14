"""
This Python script executes a series of Python scripts and subroutines that prepare input public use census geography and surname data and constructs the surname-only, georgraphy-only, and BISG proxies for race and ethnicity.

This file is set up to execute the proxy building code sequence on a set of ficitious data constructed by create_test_data.py from the publicly available census surname list and geography data. It is provided to illustrate how the main.py is set up to run the proxy building code.
"""
import os

import surname_creation_lower
import create_attr_over18_all_geo_entities



def main():

    # Identify the input directory that contains the individual or application level data containing name and geocodes.

    source_dir = "../input_files"

    # Identify the output directory for processing.
    out_dir = "../output"

    # Identify the location of the prepared input census files.
    census_data = "../input_files/created_python"

    # Run the script that prepares the analysis version of the census surname list, including the proportions of individuals by race and ethnicities by surname.
    census_surnames_lower = surname_creation_lower.create("../input_files/app_c.csv")

    create_attr_over18_all_geo_entities.create(source_dir, os.path.join(out_dir, 'created_python'))


if __name__ == '__main__':
    main()

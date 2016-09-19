"""
This program creates a fictitious sample data set based on a random sample
of records from the public use census surname list and census geography files.
Because areas spanned by ZIP codes are not necessarily nested within census geography (like tract or block group)
the ZIP code level demographic file does not contain tract or block group identifiers.
In constructing this sample data set, created solely for the purpose of illustrating how to
set up the proxy building code sequence, we select a random list of ZIP codes, which will
likely be unrelated to the tract or block groups to which they will be merged.  This
fictitious sample data cannot be used to test the accuracy of the proxy.
"""

import pandas as pd
from numpy.random import choice, seed


# Read in surname data and take a random draw of 100 individuals for
# applicant last name.

app_c = pd.read_csv('../input_files/app_c.csv')

seed(1234)

draw = choice(app_c.shape[0], app_c.shape[0], replace=False)
name1 = app_c[draw < 100].name

# Read in surname data and take a random draw of 25 invididuals for
# coapplicant last name.

seed(5678)

draw = choice(app_c.shape[0], app_c.shape[0], replace=False)
name2 = app_c[draw < 25].name

# Read in geography data from census geography files.

# Block groups are nested within tracts, so merge tract and block group codes.

tract_vars = ['GEOID10_Tract', 'State_FIPS10', 'County_FIPS10', 'Tract_FIPS10']
tract = pd.read_stata('../input_files/tract_over18_race_dec10.dta')[tract_vars]

blk_vars = ['GEOID10_BlkGrp', 'State_FIPS10',
            'County_FIPS10', 'Tract_FIPS10', 'BlkGrp_FIPS10']
blkgrp = pd.read_stata('../input_files/blkgrp_over18_race_dec10.dta')[blk_vars]

merged_geo = pd.merge(tract, blkgrp, how='left', on=[
                      'State_FIPS10', 'County_FIPS10', 'Tract_FIPS10'])

# Remove Puerto Rico
merged_geo = merged_geo[merged_geo['State_FIPS10'] != '72']

seed(91011)
draw = choice(merged_geo.shape[0], merged_geo.shape[0], replace=False)
geo_sample = merged_geo[draw < 100][['GEOID10_Tract', 'GEOID10_BlkGrp']]

# ZIP code is not strictly nested within census geography.
# Draw a random sample of ZIP codes, which likely not correspon to the
# tract and block groups above.

zip_df = pd.read_stata('../input_files/zip_over18_race_dec10.dta')

# Remove Puerto Rico
zip_df = zip_df[zip_df['ZCTA5'].apply(
    lambda x: x[:3] not in ["006", "007", "008", "009"])]

seed(121314)

draw = choice(zip_df.shape[0], zip_df.shape[0], replace=False)
zip_sample = zip_df[draw < 100]['ZCTA5']

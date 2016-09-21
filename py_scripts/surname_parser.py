import os
import re
import itertools
import pandas as pd


def read_input_data(readdir, readfile):
    return pd.read_pickle(os.path.join(readdir, readfile))


def create_record_for_coapps(df, coapp_lname, matchvars=[], keepvars=[]):
    in_vars = [coapp_lname] + matchvars + keepvars
    output = df[in_vars]
    output = output[output[coapp_lname].notnull()]
    output = output.rename(columns={coapp_lname: 'lname'})
    output['appl_coapp_cd_enum'] = 'C'
    return output


def drop_apps_without_lname(df, app_lname, matchvars=[], keepvars=[]):
    in_vars = [app_lname] + matchvars + keepvars
    output = df[in_vars]
    output = output[output[app_lname].notnull()]
    output = output.rename(columns={app_lname: 'lname'})
    output['appl_coapp_cd_enum'] = 'A'
    return output


def clean_last_names(df):
    assert 'lname' in list(df)
    df['lname'] = df['lname'].apply(lambda x: " " + x.lower() + " ")

    # Remove common non-letter, non-hyphen characters with spaces.
    no_special_chars = re.compile("[\`\{}\\,.0-9\"]")
    df['lname'] = df['lname'].apply(lambda x: no_special_chars.sub(" ", x))

    # Remove apostrophes without replacement.
    no_apostrophes = re.compile("[']")
    df['lname'] = df['lname'].apply(lambda x: no_apostrophes.sub("", x))

    #  Any lone letters in lname are most likely initials (in most cases, middle initials); remove them.
    single_letter = re.compile(" [a-z] ")
    df['lname'] = df['lname'].apply(lambda x: single_letter.sub("", x))

    # Remove common suffixes with spaces.
    suffixes = re.compile(" jr | sr | ii | iii | iv | dds | md | phd ")
    df['lname'] = df['lname'].apply(lambda x: suffixes.sub(" ", x))

    # Remove all spaces.
    single_space = re.compile("[ ]")
    df['lname'] = df['lname'].apply(lambda x: single_space.sub("", x))
    print("3. Cleaned lname in.")

    # Split hyphenated last names, then match race separately on each part.

    def min_split(x, splitter, min_len):
        out = x.split(splitter)
        if len(out) < min_len:
            out.append(None)
            return out
        else:
            return out

    df[['lname1', 'lname2']] = df['lname'].apply(lambda x: pd.Series(min_split(x, '-', 2)))
    print("4. Processed hyphens in.")

    return df


def create_race_probs_by_person(df, census, matchvars=[], keepvars=[]):
    census_keeps = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pcthispanic', 'pct2prace']

    for i in ['1', '2']:
        df = df.merge(census, how='left', left_on='lname' + i, right_on='name')
        df = df.rename(columns={c: c + i for c in census_keeps})

    out_vars = matchvars + ['appl_coapp_cd_enum'] + \
        [('').join(x) for x in itertools.product(['lname'] + census_keeps, ['1', '2'])] + \
        keepvars

    print ("5. Matched race probabilities in.")

    return df[out_vars]


def create_reshaped_race_probs_by_app(df, matchvars=[], keepvars=[]):
    assert 'appl_coapp_cd_enum' in list(df)

    def subset_by_appl_cd(df, code):

        df = df[df['appl_coapp_cd_enum'] == code.upper()]
        df = df.rename(columns={pct: code.lower() + '_' + pct for pct in list(df) if pct.startswith('pct')})
        df = df.rename(columns={keeper: code.lower() + '_' + keeper for keeper in ['lname1', 'lname2'] + keepvars})
        df = df.drop('appl_coapp_cd_enum', axis=1)

        return df

    coapps = subset_by_appl_cd(df, 'C')
    apps = subset_by_appl_cd(df, 'A')

    output = apps.merge(coapps, how='left', on=matchvars)
    print('6. Reorganized data in.')
    
    return output


def parse(app_lname, coapp_lname, output, readdir, readfile, censusdir, matchvars=[], keepvars=[]):
    print("1. Read files in.")
    input_df = read_input_data(readdir, readfile)
    print("   Loaded {:,} observations.".format(input_df.shape[0]))

    if not matchvars:
        input_df = input_df.reset_index()
        matchvars = ['index']

    # Generate a DataFrame of coapplicants
    print("2. Reformatted data.")
    coapp_df = create_record_for_coapps(input_df, coapp_lname, matchvars=matchvars, keepvars=keepvars)

    # Drop all rows without surnames and combine with coapplicant data
    app_df = drop_apps_without_lname(input_df, app_lname, matchvars=matchvars, keepvars=keepvars)
    combined_data = pd.concat([app_df, coapp_df])

    clean_data = clean_last_names(combined_data)

    # Load census data
    census_df = pd.read_pickle(os.path.join(censusdir, 'census_surnames_lower.pkl'))

    race_probs_by_person = create_race_probs_by_person(clean_data, census_df, matchvars=matchvars, keepvars=keepvars)

    reshaped_race_probs_by_app = create_reshaped_race_probs_by_app(race_probs_by_person, matchvars=matchvars, keepvars=keepvars)

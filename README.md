# BISG_RACE_ETHNICITY

In conducting fair lending analysis in both supervisory and enforcement
contexts, the Bureau’s Office of Research (OR) and Division of Supervision,
Enforcement, and Fair Lending (SEFL) rely on a Bayesian Improved Surname
Geocoding (BISG) proxy method, which combines geography- and surname-based
information into a single proxy probability for race and ethnicity used in fair
lending analysis conducted for non-mortgage products.
This document describes the steps needed to build the BISG proxies.

The methodology described here is an example of a proxy methodology that
OR and SEFL use, although we may alter this methodology in particular analyses,
depending on the circumstances involved.
In addition, the proxy method may be revised as we become aware of enhancements
that would increase accuracy and performance.
For more details, see [“Using Publicly Available Information to Proxy for
Unidentified Race and Ethnicity: A Methodology and Assessment”][paper].

Included are a series of Stata scripts and subroutines that prepare the
publicly available census geography and surname data and that construct the
surname-only, geography-only, and BISG proxies for race and ethnicity.
The scripts, subroutines, and data provided here do not contain directly
identifiable personal information or other confidential information,
such as confidential supervisory information.

Please note that all scripts and subroutines are written for execution in
STATA 12 on a Linux platform and may need to be modified for other environments.
Users must define a number of parameters, including file paths and arguments for subroutines.
The scripts that define the subroutines also identify and describe arguments, as required.

Users must supply their own application- or individual-level data,
and any geocoding of those data must occur prior to the execution of the
script sequence: **this code assumes that the input application- or
individual-level data are already geocoded with census block group,
census tract, and 5-digit ZIP code.**

However, included is an example designed to instruct the user in executing
the proxy building code sequence.
It relies on a set of fictitious data constructed by `create_test_data.do` from
the publicly available census surname list and geography data.
It is provided to illustrate how the `main.do` is set up to run the proxy
building code and does not reflect any particular individual’s or
institution’s information.

A control script, `/py_scripts/main_test_data.py`, is included to step through the process below.
The user will need to change paths and define parameters as required.

1. Build name and geography proxies from Census files included in `/input_files`:
   1. Census surname list:
      1. `/py_scripts/surname_creation_lower.py` takes .csv file of census surnames,
         formats surnames to be read as all lower case,
         and imputes any suppressed values.
         File created by `surname_creation_lower.py`:
         1. `/input_files/created_python/census_surnames_lower.pkl`
      1. In order to prepare the user-defined datasets for use with the Census surname list,
         basic cleaning of surnames using regular expressions and other forms of
         name standardization is reguired.
         This script exists at: `/py_scripts/surname_parser.py`.
         File created by `surname_parser.py` in user-defined directory:
         1. `test_output/proxy_name.pkl`
   1. Census geographies:
      1. `/py_scripts/create_attr_over18_all_geo_entities.py` uses the base information,
         for individuals age 18 and older, from the Census flat files for
         block group, tract, and ZIP code and allocates
         "Some Other Race" to each group in proportion.
         It creates three files (one each for block group, tract, and ZIP code)
         with geo probabilities for use in proxy:
         1. `/input_files/created_python/blkgrp_attr_over18.pkl`
         1. `/input_files/created_python/tract_attr_over18.pkl`
         1. `/input_files/created_python/zip_attr_over18.pkl`
1. Calculate the BISG probabilities following the methodology described in
   [“Using Publicly Available Information to Proxy for Unidentified Race and Ethnicity:
   A Methodology and Assessment”][paper].
   1. `/py_scripts/geo_name_merger_all_entities_over18.py`—this program
      creates three files (one each for block group, tract, and ZIP code)
      with BISG probabilities in a user-defined directory.
1. The final step is to merge together the block group, tract, and ZIP code-based BISG proxies
   and choose the most precise proxy given the precision of geocoding,
   e.g. block group (if available), then tract (if available), or ZIP code
   (if block group and tract unavailable).

The code contained here is inspired by the CFPB-provided Proxy Methodology stata code that is saved here: https://github.com/cfpb/proxy-methodology

Please direct all questions, comments, and suggestions to:
CFPB_proxy_methodology_comments@cfpb.gov.

---

<a aria-hidden="true" href="#fn-1" class="anchor" name="user-content-fn-1"><span class="octicon octicon-link"></span></a>
<sup>1</sup>
    When referring to ZIP code demographics, we match the institution-based
    ZIP code information to ZIP Code Tabulation Areas (ZCTAs) as defined by
    the U.S. Census Bureau.
</p>

<a aria-hidden="true" href="#fn-2" class="anchor" name="user-content-fn-2"><span class="octicon octicon-link"></span></a>
<sup>2</sup>
    In the 2010 SF1, the U.S. Census Bureau produced tabulations that report
    counts of Hispanics and non-Hispanics by race.
    These tabulations include a “Some Other Race” category.
    We reallocate the “Some Other Race” counts to each of the remaining six
    race and ethnicity categories using an Iterative Proportional Fitting
    procedure to make geography based demographic categories consistent with
    those on the census surname list.
</p>

[paper]: http://www.consumerfinance.gov/reports/using-publicly-available-information-to-proxy-for-unidentified-race-and-ethnicity/

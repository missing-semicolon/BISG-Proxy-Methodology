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

import pandas as pandas
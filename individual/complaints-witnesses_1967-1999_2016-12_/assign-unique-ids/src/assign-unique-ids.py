#!usr/bin/env python3
#
# Author(s):    Roman Rivera (Invisible Institute)

'''assign-unique-ids script for complaints-witnesses_1967-1999_2016-12_'''

import pandas as pd
import __main__

from assign_unique_ids_functions import assign_unique_ids, aggregate_data
import setup


def get_setup():
    ''' encapsulates args.
        calls setup.do_setup() which returns constants and logger
        constants contains args and a few often-useful bits in it
        including constants.write_yamlvar()
        logger is used to write logging messages
    '''
    script_path = __main__.__file__
    args = {
        'input_file': 'input/complaints-witnesses_1967-1999_2016-12.csv.gz',
        'output_file': 'output/complaints-witnesses_1967-1999_2016-12.csv.gz',
        'output_profiles_file': 'output/complaints-witnesses_1967-1999_2016-12_profiles.csv.gz',
        'id_cols': [
             'first_name_NS', 'last_name_NS', 'officer_or_non'
            ],
        'conflict_cols': [
            'middle_initial', 'suffix_name'
            ],
        'id': 'complaints-witnesses_1967-1999_2016-12_ID',
        }

    assert (args['input_file'].startswith('input/') and
            args['input_file'].endswith('.csv.gz')),\
        "input_file is malformed: {}".format(args['input_file'])
    assert (args['output_file'].startswith('output/') and
            args['output_file'].endswith('.csv.gz')),\
        "output_file is malformed: {}".format(args['output_file'])

    return setup.do_setup(script_path, args)


cons, log = get_setup()

df = pd.read_csv(cons.input_file)

df = assign_unique_ids(df, cons.id, cons.id_cols,
                       cons.conflict_cols,
                       log=log)
df.to_csv(cons.output_file, **cons.csv_opts)

profiles_df = aggregate_data(df.query("officer_or_non == 'OFFICER_WITNESS'"),
                             cons.id, cons.id_cols,
                             max_cols=cons.conflict_cols + ['star'])
profiles_df.to_csv(cons.output_profiles_file, **cons.csv_opts)

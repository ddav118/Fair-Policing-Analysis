#!usr/bin/env python3
#
# Author(s):    Roman Rivera (Invisible Institute)

'''import script for officer-filed-complaints__2017-09_p428703'''

import pandas as pd
import __main__

from import_functions import collect_metadata
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
        'input_file': 'input/tabula-FOIA_P428703_Responsive_Records.csv',
        'output_file': 'output/officer-filed-complaints__2017-09.csv.gz',
        'metadata_file': 'output/metadata_officer-filed-complaints__2017-09.csv.gz',
        'column_names_key': 'officer-filed-complaints__2017-09_p428703'
        }

    assert args['input_file'].startswith('input/'),\
        "input_file is malformed: {}".format(args['input_file'])
    assert (args['output_file'].startswith('output/') and
            args['output_file'].endswith('.csv.gz')),\
        "output_file is malformed: {}".format(args['output_file'])

    return setup.do_setup(script_path, args)


cons, log = get_setup()

df = pd.read_csv(cons.input_file, header=None)
df.columns = ['cr_id']
log.info('Only column labeled cr_id')
df.to_csv(cons.output_file, **cons.csv_opts)

meta_df = collect_metadata(df, cons.input_file, cons.output_file)
meta_df.to_csv(cons.metadata_file, **cons.csv_opts)

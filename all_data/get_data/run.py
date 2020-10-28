from .connectors.dropbox import dropbox_handler
import civis
import sys
import os
import argparse
import subprocess
from shutil import copy
import logging

LOG = logging.getLogger()


def init_args():
    """Init"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_execute',
                        default=os.environ.get('DROPBOX_PATH'))
    return parser.parse_args()


def run_make(folder_path, submodule):
    os.chdir('/'.join([folder_path, submodule]))
    makefile_path = '/'.join(['src', 'makefile'])
    LOG.info('Executing Makefile: {}'.format(makefile_path))
    subprocess.run(args=['make', '-f', makefile_path])


def get_output_filename(path):
    files = [x for x in os.listdir(path) if (
        ('.csv' in x or 'sterilized.' in x)
        and 'metadata_' not in x
        and 'missing_' not in x)]
    LOG.info("Files: {}".format(files))
    if len(files) == 1:
        return files[0]
    else:
        raise ValueError('Incorrect number of files: {}'.format(files))


def move_file_from_input_to_output(folder_path,
                                   submodule,
                                   structure):
    input_path = '/'.join([folder_path, submodule, 'output'])
    filename = get_output_filename(input_path)
    in_path = '/'.join([input_path, filename])
    if submodule == 'import':
        out_path = '/'.join([folder_path, 'clean', 'input', filename])
    if submodule == 'clean':
        if 'assign-unique-ids' in structure:
            out_path = '/'.join([folder_path, 'assign-unique-ids',
                                 'input', filename])
        else:
            out_path = '/'.join([folder_path, 'export',
                                 'input', filename])
    if submodule == 'assign-unique-ids':
        out_path = '/'.join([folder_path, 'export', 'input', filename])
    LOG.info('Moving file from: {}'.format(in_path))
    LOG.info('Moving file to: {}'.format(out_path))
    LOG.info('****************************')
    copy(in_path, out_path)


def execute_folder(folder_path):
    folder_path = folder_path.lower()
    LOG.info('Structure: {}'.format(folder_path))
    structure = os.listdir(folder_path)
    LOG.info(structure)
    if 'import' in structure:
        run_make(folder_path, 'import')
        move_file_from_input_to_output(folder_path,
                                       'import',
                                       structure)
    if 'clean' in structure:
        run_make(folder_path, 'clean')
        move_file_from_input_to_output(folder_path,
                                       'clean',
                                       structure)
    if 'assign-unique-ids' in structure:
        run_make(folder_path, 'assign-unique-ids')
        move_file_from_input_to_output(folder_path,
                                       'assign-unique-ids',
                                       structure)
    if 'export' in structure:
        run_make(folder_path, 'export')


if __name__ == "__main__":
    LOGGING_PARAMS = {
        'stream': sys.stdout,
        'level': logging.INFO,
        'format': '%(message)s'
    }

    logging.basicConfig(**LOGGING_PARAMS)
    ARGUMENTS = init_args()
    client = civis.APIClient()
    dropbox = dropbox_handler()

    # path where things are in dropbox
    dropbox.download_directory(ARGUMENTS.path_to_execute,
                               split_value=0)

    execute_folder(ARGUMENTS.path_to_execute)

    # format path_to_execute to match directory in container
    path_to_execute = ARGUMENTS.path_to_execute.lower()

    dropbox.sync_folder(path_to_execute, path_to_execute)

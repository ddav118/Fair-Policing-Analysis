import dropbox
import os
import tempfile
import pandas as pd
import logging


class dropbox_handler:
    def __init__(self):
        self.auth_token = os.environ.get('DROPBOX_OAUTH_PASSWORD')
        self.dbx = dropbox.Dropbox(self.auth_token)

    def list_files(self, dbx_path):
        res = self.dbx.files_list_folder(dbx_path)
        return [entry.name for entry in res.entries]

    def download_directory(self,
                           dbx_path,
                           split_value=5):
        res = self.dbx.files_list_folder(dbx_path, recursive=True)
        filenames = [entry.path_lower for entry in res.entries]
        if res.has_more is True:
            res2 = self.dbx.files_list_folder_continue(res.cursor)
            filenames = filenames + \
                [entry.path_lower for entry in res2.entries]
        for filename in filenames:
            logging.info('File to Download:')
            logging.info(filename)
            # get name of last filepath
            name = filename.split('/')[-1]
            github_fileloc = '/'.join(filename.split('/')[split_value:])
            if '.' not in name[1:] and name != 'makefile':
                os.makedirs(github_fileloc)
            if '.' in name[1:] or name == 'makefile':
                download_file = github_fileloc
                self.dbx.files_download_to_file(download_file, filename)

    @staticmethod
    def walk_handler(local_path):
        filenames = [filename for filename in os.walk(local_path)]
        files = []
        for filename in filenames:
            for file in filename[2]:
                files.append(filename[0]+'/'+file)
        return files

    def upload_directory(self,
                         local_path,
                         dbx_path,
                         local_dbx_same,
                         overwrite=True):
        # create output path
        if '/input' in dbx_path:
            dbx_output_path = '/'.join(dbx_path.split('/')[:-1]+['output/'])
        elif local_dbx_same is False:
            dbx_output_path = dbx_path
        else:
            dbx_output_path = local_path
        files = self.walk_handler(local_path)
        # handling dropbox required /
        if dbx_output_path[0] != '/':
            dbx_output_path = '/' + dbx_output_path
        for upload in files:
            # implies upload to individual folder
            if 'get_data/' in upload:
                relevant_path = '/'.join(upload.split('/')[4:])
                full_path = dbx_output_path+'/'+relevant_path
            # implies upload to frozen and foia
            else:
                full_path = dbx_output_path + upload.split('/')[-1]
            try:
                folder_path = '/'.join(full_path.split('/')[:-1])
                folder_path = folder_path.replace('//', '/')
                logging.info('Create Folder:')
                logging.info(folder_path)
                self.dbx.files_create_folder(folder_path)
            except:
                logging.info('Folder Exists')
            # handling possible file issues
            upload = upload.replace('//', '/')
            logging.info('File to Upload:')
            logging.info(upload)
            logging.info('Upload Path:')
            logging.info(full_path)
            logging.info('*****************')
            with open(upload, 'rb') as f:
                self.dbx.files_upload(f.read(),
                                      path=full_path,
                                      mode=dropbox.files
                                      .WriteMode('overwrite', None))

    def download_file(self,
                      dbx_path,
                      name,
                      return_sheets=False,
                      sheetname=None,
                      skip=None,
                      rows=None):
        if dbx_path[-1] != '/':
            dbx_path = dbx_path+'/'
        with tempfile.NamedTemporaryFile(mode='w') as temp:
            name = name.lower()
            download_file = dbx_path + name
            logging.info(download_file)
            self.dbx.files_download_to_file(temp.name, download_file)

            temp.flush()
            temp.seek(0)

            if return_sheets is True:
                return pd.ExcelFile(temp.name).sheet_names
            elif '.csv' in name:
                return pd.read_csv(temp.name, compression='gzip',
                                   low_memory=False)
            elif '.xls' in name:
                if sheetname is None:
                    return pd.read_excel(temp.name,
                                         skiprows=skip,
                                         nrows=rows)
                else:
                    return pd.read_excel(temp.name,
                                         sheet=sheetname,
                                         skiprows=skip,
                                         nrows=rows)
            else:
                logging.info('''Download of file not supported.
                         File is not a .csv, .xls, or .xlsx''')

    def sync_folder(self, local_directory, dropbox_directory, overwrite=True):
        """Syncs local folder contents to dropbox folder.

           Assumes directories already exist in dropbox.

           params:
            local_directory: directory from which we are uploading locally
            dropbox_directory: directory to which we are uploading in dropbox
            overwrite: whether or not to overwrite existing files
        """

        if not local_directory.endswith('/'):
            local_directory = local_directory + '/'
    
        if not dropbox_directory.endswith('/'):
            dropbox_directory = dropbox_directory + '/'

        # walk through all files/directories in local path and upload to dropbox    
        for root, dirs, files in os.walk(local_directory):

            for filename in files:
                # construct the full local path
                local_path = os.path.join(root, filename)

                # construct the full Dropbox path
                relative_path = os.path.relpath(local_path, local_directory)
                dropbox_path = os.path.join(local_directory, relative_path)

                mode = (dropbox.files.WriteMode.overwrite
                        if overwrite
                        else dropbox.files.WriteMode.add)
                
                with open(local_path, 'rb') as f:
                    data = f.read()
                try:
                    logging.info('File to upload: file:/{}'.format(local_path))
                    logging.info('Upload Path: dropbox:/{}'.format(dropbox_path))
                    res = self.dbx.files_upload(
                        data, path=dropbox_path, mode=mode)
                except dropbox.exceptions.ApiError as err:
                    logging.exception('*** API error', err)
                    return None

                                      

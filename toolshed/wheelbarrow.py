from datetime import datetime
from subprocess import call, CalledProcessError

from toolshed.tool import Tool

import os
import shutil


class Wheelbarrow(Tool):
    def __init__(self, backup_path, plone_path, **options):
        """Plone backup tool

        Arguments:
            backup_path {string} -- Path to store the backup files
            plone_path {string} -- Path to the `zeocluster` folder
            **options {dict} -- additional backup options
        """
        self.backup_path = backup_path
        self.combined = options.get('combined', True)
        self.file_group = options.get('file_group', None)
        self.file_user = options.get('file_user', None)
        self.plone_path = plone_path
        self.today = datetime.now()
        self.verbosity = options.get('verbosity', 1)


    def backup(self):
        """Backup the Plone data files"""
        self.write(
            'Plone backup for ({}) started on: {}\n'.format(
                self.plone_path,
                self.today.strftime("%-m/%-d/%Y %H:%M"),
            ),
            verbosity=1,
        )

        # backup the data.fs file
        self.write('Backing up the data.fs file', verbosity=1)
        self.copy_datafs()

        # backup the blob storage files
        self.write('Backing up the blob storage', verbosity=1)
        self.backup_blob_storage()

        date_str = self.today.strftime('%Y-%m-%d')
        if self.combined:
            files = [
                os.path.join(self.backup_path, '{}.tar.gz'.format(date_str)),
            ]
        else:
            files = [
                os.path.join(self.backup_path, '{}_data.fs'.format(date_str)),
                os.path.join(self.backup_path, '{}_blobstorage.tar.gz'.format(date_str)),  # NOQA
            ]

        # fix the permissions on the backup file
        for file in files:
            call(['chmod', '440', file])

        # update backup file ownership
        if self.file_group is not None:
            for file in files:
                call(['chgrp', self.file_group, file])
        if self.file_user is not None:
            for file in files:
                call(['chown', self.file_user, file])

        # output the completion stats
        self.write(
            '\nBackup finished on {}\n'.format(
                datetime.now().strftime('%-m/%-d/%Y %H:%M')
            ),
            verbosity=1
        )


    def backup_blob_storage(self):
        """Backup the Plone blob storage by tarring the files"""
        filename = '{}{}.tar.gz'.format(
            self.today.strftime('%Y-%m-%d'),
            '' if self.combined else '_blobstorage'
        )
        blob_path = os.path.join(self.plone_path, 'var', 'blobstorage')
        cmd = 'tar -cz .layout *'
        try:
            with open(os.path.join(self.backup_path, filename), 'wb') as out_file:  # NOQA
                call(cmd, shell=True, stdout=out_file, cwd=blob_path)
        except CalledProcessError:
            pass
        else:
            if self.combined:
                shutil.rmtree(os.path.join(blob_path, 'Data.fs'), ignore_errors=True)  # NOQA


    def copy_datafs(self):
        """Copy the Plone data.fs file and prefix with the current date"""
        datafs_path = os.path.join(self.plone_path, 'var', 'filestorage')
        src_file = os.path.join(datafs_path, 'Data.fs')
        if self.combined:
            dest_file = os.path.join(self.plone_path, 'var', 'blobstorage', 'Data.fs')  # NOQA
        if not self.combined:
            filename = '{}_data.fs'.format(self.today.strftime('%Y-%m-%d'))
            dest_file = os.path.join(self.backup_path, filename)
        shutil.copyfile(src_file, dest_file)




if __name__ == '__main__':
    ### TODO: implement argparse and a proper call to bucket.backup()
    wheelbarrow = Wheelbarrow('./', '/opt/current-plone/zeocluster')
    wheelbarrow.backup()

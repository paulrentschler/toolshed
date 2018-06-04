from datetime import datetime
from subprocess import call

from toolshed.wheelbarrow import Wheelbarrow

import os
import shutil
import unittest
import uuid


class TestBucket(unittest.TestCase):

    def create_dir(self, suffix=''):
        """Create a temporary directory to use for the tests

        A random character directory name will be created in the current
        working directory.

        KEYWORD ARGUMENTS:
            suffix {string} -- text to add to the end of the directory name
                               (default: {''})

        Returns:
            {string} -- complete path for the temporary directory
        """
        while 2:
            tmp_dir = uuid.uuid4().hex[:8]
            if suffix:
                tmp_dir = "{}_{}".format(tmp_dir, suffix)
            tmp_path = os.path.join('.', tmp_dir)
            if os.path.exists(tmp_path):
                continue
            os.makedirs(tmp_path)
            return tmp_path


    def remove_dir(self, path):
        """Remove the directory and all of it's contents

        Arguments:
            path {string} -- complete path to the directory to remove
        """
        shutil.rmtree(path, ignore_errors=True)


    def test_backup_combined(self):
        """Test backing up the Plone data into a single file"""
        tmp_path = self.create_dir('combined')
        wheelbarrow = Wheelbarrow(
            tmp_path,
            os.path.join('/', 'opt', 'current-plone', 'zeocluster'),
            verbosity=0,
            combined=True
        )
        wheelbarrow.backup()

        backup_date = datetime.now().strftime("%Y-%m-%d")
        self.assertTrue(
            os.path.isfile(os.path.join(tmp_path, backup_date + '.tar.gz')),
            msg='Backup file was not created'
        )
        backup_dir = os.path.join(tmp_path, backup_date)
        os.makedirs(backup_dir)
        call(
            ['tar', '-zxmf', os.path.join('..', backup_date + '.tar.gz')],
            cwd=backup_dir
        )
        self.assertTrue(
            os.path.isfile(os.path.join(backup_dir, 'Data.fs')),
            msg='Backup Data.fs file not included in backup'
        )
        self.assertTrue(
            os.path.isfile(os.path.join(backup_dir, '.layout')),
            msg='Backup blob storage layout file not included in backup'
        )
        self.assertTrue(
            'tmp' in os.listdir(backup_dir),
            msg='Backup of blob storage incomplete'
        )
        self.remove_dir(tmp_path)


    def test_backup_separate(self):
        """Test backing up the Plone data into multiple files"""
        tmp_path = self.create_dir('separate')
        wheelbarrow = Wheelbarrow(
            tmp_path,
            os.path.join('/', 'opt', 'current-plone', 'zeocluster'),
            verbosity=0,
            combined=False
        )
        wheelbarrow.backup()

        backup_date = datetime.now().strftime("%Y-%m-%d")
        self.assertTrue(
            os.path.isfile(os.path.join(tmp_path, backup_date + '_data.fs')),
            msg='Backup Data.fs file was not created'
        )
        self.assertTrue(
            os.path.isfile(os.path.join(tmp_path, backup_date + '_blobstorage.tar.gz')),  # NOQA
            msg='Backup blob storage file was not created'
        )
        backup_dir = os.path.join(tmp_path, backup_date)
        os.makedirs(backup_dir)
        call(
            ['tar', '-zxmf', os.path.join('..', backup_date + '_blobstorage.tar.gz')],  # NOQA
            cwd=backup_dir
        )
        self.assertTrue(
            os.path.isfile(os.path.join(backup_dir, '.layout')),
            msg='Backup blob storage layout file not included in backup'
        )
        self.assertTrue(
            'tmp' in os.listdir(backup_dir),
            msg='Backup of blob storage incomplete'
        )
        self.assertFalse(
            'Data.fs' in os.listdir(backup_dir),
            msg='Backup Data.fs file was in blob storage backup'
        )
        self.remove_dir(tmp_path)




if __name__ == '__main__':
    unittest.main()

from datetime import date, timedelta

from toolshed.shears import Shears

import os
import shutil
import unittest
import uuid


class TestStringMethods(unittest.TestCase):

    def create_files(self, start_date, num_files, extension, name_suffix=''):
        """Create sequential backup files

        [description]

        Arguments:
            start_date {date} -- Starting date for the first backup file
            num_files {integer} -- Total number of backup files to create
            extension {string} -- Filename extension to use

        Keyword Arguments:
            name_suffix {string} -- Optional suffix to add to the filename
                                    (Default: '')
        """
        extension = extension.replace('.', '')
        while num_files > 0:
            filename = '{:04d}-{:02d}-{:02d}'.format(
                start_date.year,
                start_date.month,
                start_date.day
            )
            if name_suffix:
                filename = '{}_{}'.format(filename, name_suffix)
            filename = '{}.{}'.format(filename, extension)
            open(os.path.join(self.tmp_path, 'daily', filename), 'a').close()
            start_date = start_date + timedelta(days=1)
            num_files -= 1


    def setUp(self):
        """Create a temporary directory structure to use for the pruning tests

        A random character directory name will be created in the current
        working directory and then four directories (daily, weekly, monthly,
        and yearly) will be created within that directory.

        `self.tmp_path` references the temporary directory path
        """
        while 2:
            tmp_dir = uuid.uuid4().hex[:8]
            self.tmp_path = os.path.join('.', tmp_dir)
            if os.path.exists(self.tmp_path):
                continue
            os.makedirs(self.tmp_path)
            break
        for level in ('daily', 'weekly', 'monthly', 'yearly'):
            path = os.path.join(self.tmp_path, level)
            os.makedirs(path)


    def tearDown(self):
        """Delete the temporary directory and everything it contains"""
        shutil.rmtree(self.tmp_path, ignore_errors=True)


    def test_everything(self):
        """Prune nine months of files that span the end of the year

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', 'test_backup')
        shears = Shears(self.tmp_path, '.bak')
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [
                '2018-08-03_test_backup.bak',
                '2018-08-04_test_backup.bak',
                '2018-08-05_test_backup.bak',
                '2018-08-06_test_backup.bak',
                '2018-08-07_test_backup.bak',
                '2018-08-08_test_backup.bak',
                '2018-08-09_test_backup.bak',
                '2018-08-10_test_backup.bak',
                '2018-08-11_test_backup.bak',
                '2018-08-12_test_backup.bak',
                '2018-08-13_test_backup.bak',
                '2018-08-14_test_backup.bak',
                '2018-08-15_test_backup.bak',
                '2018-08-16_test_backup.bak',
            ],
            msg='Daily files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'weekly'))),
            [
                '2018-06-23_test_backup.bak',
                '2018-06-30_test_backup.bak',
                '2018-07-07_test_backup.bak',
                '2018-07-14_test_backup.bak',
                '2018-07-21_test_backup.bak',
                '2018-07-28_test_backup.bak',
            ],
            msg='Weekly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-01-31_test_backup.bak',
                '2018-02-28_test_backup.bak',
                '2018-03-31_test_backup.bak',
                '2018-04-30_test_backup.bak',
                '2018-05-31_test_backup.bak',
                '2018-07-31_test_backup.bak',
            ],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            ['2017-12-31_test_backup.bak', ],
            msg='Yearly files do not match the expected files'
        )


if __name__ == '__main__':
    unittest.main()

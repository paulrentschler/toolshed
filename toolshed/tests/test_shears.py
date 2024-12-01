from datetime import date, timedelta

from toolshed.shears import Shears

import os
import shutil
import unittest
import uuid


class TestShears(unittest.TestCase):

    def create_files(self, start_date, num_files, extension, name_suffix=''):
        """Create sequential backup files

        Arguments:
            start_date {date} -- Starting date for the first backup file
            num_files {integer} -- Total number of backup files to create
            extension {string} -- Filename extension to use

        Keyword Arguments:
            name_suffix {string} -- Optional suffix to add to the filename
                                    (Default: '')
        """
        if extension[0] == '.':
            extension = extension[1:]
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
        error_free = True
        for error in self._outcome.errors:
            if error[1] is not None:
                error_free = False
        if error_free:
            shutil.rmtree(self.tmp_path, ignore_errors=True)

    def test_default(self):
        """Prune nine months of files that span the end of the year

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', 'test_backup')
        shears = Shears(self.tmp_path, ['.bak', ], verbosity=0)
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

    def test_just_dates(self):
        """Prune nine months of files that just have dates for filenames

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', '')
        shears = Shears(self.tmp_path, ['.bak', ], verbosity=0)
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [
                '2018-08-03.bak',
                '2018-08-04.bak',
                '2018-08-05.bak',
                '2018-08-06.bak',
                '2018-08-07.bak',
                '2018-08-08.bak',
                '2018-08-09.bak',
                '2018-08-10.bak',
                '2018-08-11.bak',
                '2018-08-12.bak',
                '2018-08-13.bak',
                '2018-08-14.bak',
                '2018-08-15.bak',
                '2018-08-16.bak',
            ],
            msg='Daily files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'weekly'))),
            [
                '2018-06-23.bak',
                '2018-06-30.bak',
                '2018-07-07.bak',
                '2018-07-14.bak',
                '2018-07-21.bak',
                '2018-07-28.bak',
            ],
            msg='Weekly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-01-31.bak',
                '2018-02-28.bak',
                '2018-03-31.bak',
                '2018-04-30.bak',
                '2018-05-31.bak',
                '2018-07-31.bak',
            ],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            ['2017-12-31.bak', ],
            msg='Yearly files do not match the expected files'
        )

    def test_shorter_limits(self):
        """Prune nine months of files that span the end of the year

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories with non-default limits on the number of files:
            daily: 20
            weekly: 4
            monthly: 3
            yearly: 2
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', 'test_backup')
        shears = Shears(
            self.tmp_path,
            ['.bak', ],
            verbosity=0,
            daily=20,
            weekly=4,
            monthly=3,
            yearly=2,
        )
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [
                '2018-07-28_test_backup.bak',
                '2018-07-29_test_backup.bak',
                '2018-07-30_test_backup.bak',
                '2018-07-31_test_backup.bak',
                '2018-08-01_test_backup.bak',
                '2018-08-02_test_backup.bak',
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
                '2018-06-30_test_backup.bak',
                '2018-07-07_test_backup.bak',
                '2018-07-14_test_backup.bak',
                '2018-07-21_test_backup.bak',
            ],
            msg='Weekly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-03-31_test_backup.bak',
                '2018-04-30_test_backup.bak',
                '2018-05-31_test_backup.bak',
            ],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            ['2017-12-31_test_backup.bak', ],
            msg='Yearly files do not match the expected files'
        )

    def test_daily_weekly_only(self):
        """Prune nine months of files that span the end of the year

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily and weekly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', 'test_backup')
        shears = Shears(
            self.tmp_path,
            ['.bak', ],
            verbosity=0,
            monthly=0,
            yearly=0,
        )
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
            [],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            [],
            msg='Yearly files do not match the expected files'
        )

    def test_multiple_extensions(self):
        """Prune nine months of files with three different extensions

        Takes nine months worth of files with three different extensions,
        spanning from 15 Nov 2017 till 16 Aug 2018, and prunes them into
        daily, weekly, monthly, and yearly directories with less than the
        default limits for each level.
        """
        self.create_files(date(2017, 11, 15), 275, '.back.up', 'test_backup')
        self.create_files(date(2017, 11, 15), 275, '.tmp.bak', 'test_backup')
        self.create_files(date(2017, 11, 15), 275, '.tmp', 'test_backup')
        shears = Shears(
            self.tmp_path,
            ['up', '.bak', 'tmp'],
            verbosity=0,
            daily=7,
            weekly=2,
            monthly=2,
            yearly=2,
        )
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [
                '2018-08-10_test_backup.back.up',
                '2018-08-10_test_backup.tmp',
                '2018-08-10_test_backup.tmp.bak',
                '2018-08-11_test_backup.back.up',
                '2018-08-11_test_backup.tmp',
                '2018-08-11_test_backup.tmp.bak',
                '2018-08-12_test_backup.back.up',
                '2018-08-12_test_backup.tmp',
                '2018-08-12_test_backup.tmp.bak',
                '2018-08-13_test_backup.back.up',
                '2018-08-13_test_backup.tmp',
                '2018-08-13_test_backup.tmp.bak',
                '2018-08-14_test_backup.back.up',
                '2018-08-14_test_backup.tmp',
                '2018-08-14_test_backup.tmp.bak',
                '2018-08-15_test_backup.back.up',
                '2018-08-15_test_backup.tmp',
                '2018-08-15_test_backup.tmp.bak',
                '2018-08-16_test_backup.back.up',
                '2018-08-16_test_backup.tmp',
                '2018-08-16_test_backup.tmp.bak',
            ],
            msg='Daily files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'weekly'))),
            [
                '2018-07-28_test_backup.back.up',
                '2018-07-28_test_backup.tmp',
                '2018-07-28_test_backup.tmp.bak',
                '2018-08-04_test_backup.back.up',
                '2018-08-04_test_backup.tmp',
                '2018-08-04_test_backup.tmp.bak',
            ],
            msg='Weekly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-06-30_test_backup.back.up',
                '2018-06-30_test_backup.tmp',
                '2018-06-30_test_backup.tmp.bak',
                '2018-07-31_test_backup.back.up',
                '2018-07-31_test_backup.tmp',
                '2018-07-31_test_backup.tmp.bak',
            ],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            [
                '2017-12-31_test_backup.back.up',
                '2017-12-31_test_backup.tmp',
                '2017-12-31_test_backup.tmp.bak',
            ],
            msg='Yearly files do not match the expected files'
        )

    def test_daily_monthly_only(self):
        """Prune nine months of files that span the end of the year

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily and monthly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', 'test_backup')
        shears = Shears(
            self.tmp_path,
            ['.bak', ],
            verbosity=0,
            daily=14,
            weekly=0,
            monthly=6,
            yearly=0,
        )
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
            [],
            msg='Weekly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-02-28_test_backup.bak',
                '2018-03-31_test_backup.bak',
                '2018-04-30_test_backup.bak',
                '2018-05-31_test_backup.bak',
                '2018-06-30_test_backup.bak',
                '2018-07-31_test_backup.bak',
            ],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            [],
            msg='Yearly files do not match the expected files'
        )

    def test_monthly_only(self):
        """Prune nine months of files that span the end of the year

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into monthly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', 'test_backup')
        shears = Shears(
            self.tmp_path,
            ['.bak', ],
            verbosity=0,
            daily=0,
            weekly=0,
            monthly=6,
            yearly=0,
        )
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [],
            msg='Daily files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'weekly'))),
            [],
            msg='Weekly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-02-28_test_backup.bak',
                '2018-03-31_test_backup.bak',
                '2018-04-30_test_backup.bak',
                '2018-05-31_test_backup.bak',
                '2018-06-30_test_backup.bak',
                '2018-07-31_test_backup.bak',
            ],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            [],
            msg='Yearly files do not match the expected files'
        )

    def test_limit_multipart_extension(self):
        """Prune 10 files with multipart extensions down to 6"""
        self.create_files(date(2017, 11, 15), 10, '.tmp.bak', 'test_backup')
        for item in os.listdir(os.path.join(self.tmp_path, 'daily')):
            src = os.path.join(self.tmp_path, 'daily', item)
            dest = os.path.join(self.tmp_path, item)
            os.rename(src, dest)
        for folder in ['daily', 'weekly', 'monthly', 'yearly']:
            shutil.rmtree(
                os.path.join(self.tmp_path, folder),
                ignore_errors=True
            )

        shears = Shears(self.tmp_path, ['.bak', ], verbosity=0, limit=6)
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(self.tmp_path)),
            [
                '2017-11-19_test_backup.tmp.bak',
                '2017-11-20_test_backup.tmp.bak',
                '2017-11-21_test_backup.tmp.bak',
                '2017-11-22_test_backup.tmp.bak',
                '2017-11-23_test_backup.tmp.bak',
                '2017-11-24_test_backup.tmp.bak',
            ],
            msg='Remaining files do not match the expected files'
        )

    def test_limit_only(self):
        """Prune 10 files down to 6"""
        self.create_files(date(2017, 11, 15), 10, '.bak', 'test_backup')
        for item in os.listdir(os.path.join(self.tmp_path, 'daily')):
            src = os.path.join(self.tmp_path, 'daily', item)
            dest = os.path.join(self.tmp_path, item)
            os.rename(src, dest)
        for folder in ['daily', 'weekly', 'monthly', 'yearly']:
            shutil.rmtree(
                os.path.join(self.tmp_path, folder),
                ignore_errors=True
            )

        shears = Shears(self.tmp_path, ['.bak', ], verbosity=0, limit=6)
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(self.tmp_path)),
            [
                '2017-11-19_test_backup.bak',
                '2017-11-20_test_backup.bak',
                '2017-11-21_test_backup.bak',
                '2017-11-22_test_backup.bak',
                '2017-11-23_test_backup.bak',
                '2017-11-24_test_backup.bak',
            ],
            msg='Remaining files do not match the expected files'
        )


if __name__ == '__main__':
    unittest.main()

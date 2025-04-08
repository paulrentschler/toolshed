from datetime import date, timedelta

from toolshed.shears import Shears

import os
import shutil
import unittest
import uuid


class TestShears(unittest.TestCase):

    def create_files(self, start_date, num_files, extension, name_suffix='',
                     alt_date_format=False):
        """Create sequential backup files

        Arguments:
            start_date {date} -- Starting date for the first backup file
            num_files {integer} -- Total number of backup files to create
            extension {string} -- Filename extension to use

        Keyword Arguments:
            name_suffix {string} -- Optional suffix to add to the filename
                                    (Default: '')
            alt_date_format {bool} -- Toggle between the normal YYYY-MM-DD
                                      date format and the alternative
                                      YYYYMMDD format (default: False which
                                      uses the normal YYYY-MM-DD format)
        """
        if alt_date_format:
            date_format = '{:04d}{:02d}{:02d}'
            separator = '-'
        else:
            date_format = '{:04d}-{:02d}-{:02d}'
            separator = '_'
        if extension[0] == '.':
            extension = extension[1:]
        while num_files > 0:
            filename = date_format.format(
                start_date.year,
                start_date.month,
                start_date.day
            )
            if name_suffix:
                filename = '{}{}{}'.format(filename, separator, name_suffix)
            filename = '{}.{}'.format(filename, extension)
            open(os.path.join(self.tmp_path, 'daily', filename), 'a').close()
            start_date = start_date + timedelta(days=1)
            num_files -= 1

    def create_folders(self, start_date, num_folders, name_suffix='',
                       alt_date_format=False):
        """Create sequential backup folders

        Arguments:
            start_date {date} -- Starting date for the first backup file
            num_folders {integer} -- Total number of backup files to create

        Keyword Arguments:
            name_suffix {string} -- Optional suffix to add to the folder name
                                    (Default: '')
        """
        if alt_date_format:
            date_format = '{:04d}{:02d}{:02d}'
            separator = '-'
        else:
            date_format = '{:04d}-{:02d}-{:02d}'
            separator = '_'
        while num_folders > 0:
            folder_name = date_format.format(
                start_date.year,
                start_date.month,
                start_date.day
            )
            if name_suffix:
                folder_name = '{}{}{}'.format(
                    folder_name,
                    separator,
                    name_suffix
                )
            path = os.path.join(self.tmp_path, 'daily', folder_name)
            os.mkdir(path)
            open(os.path.join(path, 'test.bak'), 'a').close()
            open(os.path.join(path, 'test.log'), 'a').close()
            open(os.path.join(path, 'test.tar.gz'), 'a').close()
            open(os.path.join(path, 'test.zip'), 'a').close()
            start_date = start_date + timedelta(days=1)
            num_folders -= 1

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

    def test_directory__levels(self):
        """Prune nine months of folders that span the end of the year

        Takes nine months worth of folders, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories.
        """
        self.create_folders(date(2017, 11, 15), 275, 'backup')
        shears = Shears(
            self.tmp_path,
            ['', ],
            folders=True,
            verbosity=0,
        )
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [
                '2018-08-03_backup',
                '2018-08-04_backup',
                '2018-08-05_backup',
                '2018-08-06_backup',
                '2018-08-07_backup',
                '2018-08-08_backup',
                '2018-08-09_backup',
                '2018-08-10_backup',
                '2018-08-11_backup',
                '2018-08-12_backup',
                '2018-08-13_backup',
                '2018-08-14_backup',
                '2018-08-15_backup',
                '2018-08-16_backup',
            ],
            msg='Daily folders do not match the expected folders'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'weekly'))),
            [
                '2018-06-23_backup',
                '2018-06-30_backup',
                '2018-07-07_backup',
                '2018-07-14_backup',
                '2018-07-21_backup',
                '2018-07-28_backup',
            ],
            msg='Weekly folders do not match the expected folders'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-01-31_backup',
                '2018-02-28_backup',
                '2018-03-31_backup',
                '2018-04-30_backup',
                '2018-05-31_backup',
                '2018-07-31_backup',
            ],
            msg='Monthly folders do not match the expected folders'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            ['2017-12-31_backup', ],
            msg='Yearly folders do not match the expected folders'
        )

    def test_directory__limit(self):
        """Prune 10 directories down to 6"""
        self.create_folders(date(2017, 11, 15), 10)
        for item in os.listdir(os.path.join(self.tmp_path, 'daily')):
            src = os.path.join(self.tmp_path, 'daily', item)
            dest = os.path.join(self.tmp_path, item)
            os.rename(src, dest)
        for folder in ['daily', 'weekly', 'monthly', 'yearly']:
            shutil.rmtree(
                os.path.join(self.tmp_path, folder),
                ignore_errors=True
            )

        shears = Shears(
            self.tmp_path,
            ['', ],
            folders=True,
            limit=6,
            verbosity=0,
        )
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(self.tmp_path)),
            [
                '2017-11-19',
                '2017-11-20',
                '2017-11-21',
                '2017-11-22',
                '2017-11-23',
                '2017-11-24',
            ],
            msg='Remaining folders do not match the expected folders'
        )

    def test_directory_alt__levels(self):
        """Prune nine months of folders that span the end of the year

        Uses the alternate date format

        Takes nine months worth of folders, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories.
        """
        self.create_folders(
            date(2017, 11, 15),
            275,
            'backup',
            alt_date_format=True
        )
        shears = Shears(
            self.tmp_path,
            ['', ],
            folders=True,
            verbosity=0,
        )
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [
                '20180803-backup',
                '20180804-backup',
                '20180805-backup',
                '20180806-backup',
                '20180807-backup',
                '20180808-backup',
                '20180809-backup',
                '20180810-backup',
                '20180811-backup',
                '20180812-backup',
                '20180813-backup',
                '20180814-backup',
                '20180815-backup',
                '20180816-backup',
            ],
            msg='Daily folders do not match the expected folders'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'weekly'))),
            [
                '20180623-backup',
                '20180630-backup',
                '20180707-backup',
                '20180714-backup',
                '20180721-backup',
                '20180728-backup',
            ],
            msg='Weekly folders do not match the expected folders'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '20180131-backup',
                '20180228-backup',
                '20180331-backup',
                '20180430-backup',
                '20180531-backup',
                '20180731-backup',
            ],
            msg='Monthly folders do not match the expected folders'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            ['20171231-backup', ],
            msg='Yearly folders do not match the expected folders'
        )

    def test_directory_alt__limit(self):
        """Prune 10 directories down to 6

        Uses the alternate date format
        """
        self.create_folders(date(2017, 11, 15), 10, alt_date_format=True)
        for item in os.listdir(os.path.join(self.tmp_path, 'daily')):
            src = os.path.join(self.tmp_path, 'daily', item)
            dest = os.path.join(self.tmp_path, item)
            os.rename(src, dest)
        for folder in ['daily', 'weekly', 'monthly', 'yearly']:
            shutil.rmtree(
                os.path.join(self.tmp_path, folder),
                ignore_errors=True
            )

        shears = Shears(
            self.tmp_path,
            ['', ],
            folders=True,
            limit=6,
            verbosity=0,
        )
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(self.tmp_path)),
            [
                '20171119',
                '20171120',
                '20171121',
                '20171122',
                '20171123',
                '20171124',
            ],
            msg='Remaining folders do not match the expected folders'
        )

    def test_just_dates(self):
        """Prune nine months of files that just have dates for filenames

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.bak', '')
        shears = Shears(self.tmp_path, ['.bak ', ], verbosity=0)
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

    def test_just_dates__multipart_extension(self):
        """Prune nine months of files with YYYY-MM-DD.tar.gz filenames

        Takes nine months worth of files, spanning from 15 Nov 2017 till
        16 Aug 2018, and prunes them into daily, weekly, monthly, and
        yearly directories.
        """
        self.create_files(date(2017, 11, 15), 275, '.tar.gz', '')
        shears = Shears(self.tmp_path, ['tar.gz', ], verbosity=0)
        shears.prune()
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'daily'))),
            [
                '2018-08-03.tar.gz',
                '2018-08-04.tar.gz',
                '2018-08-05.tar.gz',
                '2018-08-06.tar.gz',
                '2018-08-07.tar.gz',
                '2018-08-08.tar.gz',
                '2018-08-09.tar.gz',
                '2018-08-10.tar.gz',
                '2018-08-11.tar.gz',
                '2018-08-12.tar.gz',
                '2018-08-13.tar.gz',
                '2018-08-14.tar.gz',
                '2018-08-15.tar.gz',
                '2018-08-16.tar.gz',
            ],
            msg='Daily files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'weekly'))),
            [
                '2018-06-23.tar.gz',
                '2018-06-30.tar.gz',
                '2018-07-07.tar.gz',
                '2018-07-14.tar.gz',
                '2018-07-21.tar.gz',
                '2018-07-28.tar.gz',
            ],
            msg='Weekly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'monthly'))),
            [
                '2018-01-31.tar.gz',
                '2018-02-28.tar.gz',
                '2018-03-31.tar.gz',
                '2018-04-30.tar.gz',
                '2018-05-31.tar.gz',
                '2018-07-31.tar.gz',
            ],
            msg='Monthly files do not match the expected files'
        )
        self.assertListEqual(
            sorted(os.listdir(os.path.join(self.tmp_path, 'yearly'))),
            ['2017-12-31.tar.gz', ],
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
            ['back.up', '.tmp.bak', 'tmp'],
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

        shears = Shears(self.tmp_path, [' tmp.bak ', ], verbosity=0, limit=6)
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

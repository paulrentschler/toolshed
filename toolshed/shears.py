#!/usr/bin/env python

from collections import OrderedDict
from datetime import datetime, timedelta

from toolshed.tool import BaseCommand, CommandError, Tool

import os
import sys


class Shears(Tool):
    def __init__(self, backup_path, file_extensions, **options):
        """Backup file pruning tool

        Arguments:
            backup_path {string} -- Path where backup files are stored
            file_extensions {list} -- List of file extensions of backup
                                      files to prune
            **options {dict} -- additional pruning options
        """
        self.backup_levels = OrderedDict()
        self.backup_path = backup_path
        self.dryrun = options.get('dryrun', False)
        self.file_extensions = [
            ext.strip().replace('.', '') for ext in file_extensions
        ]
        self.today = datetime.now()
        self.verbosity = options.get('verbosity', 1)

        # set default level options
        if 'daily' not in options.keys():
            options['daily'] = 14
        if 'weekly' not in options.keys():
            options['weekly'] = 6
        if 'monthly' not in options.keys():
            options['monthly'] = 6
        if 'yearly' not in options.keys():
            options['yearly'] = 6

        # set the backup levels, max files, and paths
        for level in ('daily', 'weekly', 'monthly', 'yearly'):
            try:
                days = options.get(level, 0)
            except KeyError:
                continue
            self.backup_levels[level] = {
                'limit': days,
                'path': os.path.join(self.backup_path, level),
            }


    def delete(self, filename, extension, path):
        """Delete existing backup file

        Arguments:
            filename {string} -- Backup filename without the extension
                                 in the format YYYY-MM-DD
            extension {string} -- Extension for the backup file
            path {string} -- Path to the backup file
        """
        filename = "{}.{}".format(filename, extension)
        filename = os.path.join(path, filename)
        self.write('{}        Deleting {}'.format(
            'DryRun: ' if self.dryrun else '',
            filename,
        ), verbosity=3)
        if not self.dryrun:
            os.remove(filename)


    def get_backup_date(self, filename):
        """Returns datetime object based on the date in the filename

        `filename` must be in the format YYYY-MM-DD with any additional
        part of the filename following _ after the date.

        Examples:
            YYYY-MM-DD
            YYYY-MM-DD_database
            YYYY-MM-DD_database_test

        Arguments:
            filename {string} -- backup filename without the extension
                                 in the format YYYY-MM-DD_extra_text

        Returns:
            {datetime} -- datetime object based on the date in the filename
                          or None if filename doesn't translate to a date
        """
        try:
            file_date, file_description = filename.split('_', 1)
        except ValueError:
            file_date = filename
        try:
            return datetime.strptime(file_date, "%Y-%m-%d")
        except ValueError:
            return None


    def is_end_of(self, timeframe, filename):
        """Is the `filename` at the end of the `timeframe`

        Arguments:
            timeframe {string} -- Period of time being checked (i.e., weekly)
            filename {string} -- Backup file's name without extension
                                 in the format YYYY-MM-DD_extra_text

        Returns:
            {boolean} -- If the date of the filename is at the end of the
                         timeframe
        """
        file_date = self.get_backup_date(filename)
        year = int(file_date.strftime("%Y"))
        if timeframe == 'weekly':
            # Saturday (6) is considered the end of the week
            return file_date.strftime("%w") == '6'
        elif timeframe == 'monthly':
            month = int(file_date.strftime("%-m")) + 1
            if month == 13:
                year += 1
                month = 1
            test_date = datetime(year, month, 1) - timedelta(days=1)
            return file_date == test_date
        elif timeframe == 'yearly':
            test_date = datetime(year, 12, 31)
            return file_date == test_date
        return False


    def move(self, filename, extension, path, new_path):
        """Move backup file to a new level

        Arguments:
            filename {string} -- Backup filename without the extension
                                 in the format YYYY-MM-DD
            extension {string} -- Extension for the backup file
            path {string} -- Path to the backup file
            new_path {string} -- Path where the backup file is going
        """
        filename = "{}.{}".format(filename, extension)
        src = os.path.join(path, filename)
        dest = os.path.join(new_path, filename)
        self.write('{}        Renaming {} to {}'.format(
            'DryRun: ' if self.dryrun else '',
            src,
            dest,
        ), verbosity=3)
        if not self.dryrun:
            os.rename(src, dest)


    def prune(self):
        """Starting point to prune backups at all levels"""
        self.write('{}Pruning backups in ({}) started on: {}\n'.format(
            'DryRun: ' if self.dryrun else '',
            self.backup_path,
            self.today.strftime("%-m/%-d/%Y %H:%M"),
        ), verbosity=1)

        for level, details in self.backup_levels.items():
            for extension in self.file_extensions:
                self.prune_level(
                    extension,
                    level,
                    details['path'],
                    details['limit']
                )

        # output the completion stats
        self.write('\n{}Pruning finished on {}\n'.format(
            'DryRun: ' if self.dryrun else '',
            datetime.now().strftime('%-m/%-d/%Y %H:%M'),
        ), verbosity=1)


    def prune_level(self, file_extension, level, path, limit):
        """Prune the files at one backup level

        Arguments:
            file_extension {string} -- Extension of backup files to prune
            level {string} -- Backup level to process
            path {object} -- Path to the files in the backup level
            limit {integer} -- Number of days worth of backups to keep
                               for this backup level
        """
        self.write('{}Prune {} *.{} files ({} max)'.format(
            'DryRun: ' if self.dryrun else '',
            level,
            file_extension,
            limit,
        ), verbosity=1)

        # read the valid backup files from `path`
        self.write('{}    Obtain the existing backup files'.format(
            'DryRun: ' if self.dryrun else '',
        ), verbosity=2)
        backup_files = []
        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):
                self.write('{}        Skipping {}: not a file'.format(
                    'DryRun: ' if self.dryrun else '',
                    os.path.join(path, item),
                ), verbosity=3)
                continue
            filename, extension = item.rsplit('.', 1)
            if extension != file_extension:
                self.write('{}        Skipping {}: not *.{} file'.format(
                    'DryRun: ' if self.dryrun else '',
                    os.path.join(path, item),
                    file_extension,
                ), verbosity=3)
                continue
            if self.get_backup_date(filename) is None:
                self.write('{}        Skipping {}: no date in filename'.format(  # NOQA
                    'DryRun: ' if self.dryrun else '',
                    os.path.join(path, item),
                ), verbosity=3)
                continue
            else:
                self.write('{}        Keeping {}'.format(
                    'DryRun: ' if self.dryrun else '',
                    os.path.join(path, item),
                ), verbosity=3)
                backup_files.append(filename)

        # identify the files to remove
        backup_files.sort()
        remove_files = []
        while len(backup_files) > limit:
            remove_files.append(backup_files.pop(0))

        # remove the files for this level
        levels = list(self.backup_levels.keys())
        level_index = levels.index(level)
        for backup_file in remove_files:
            moved = False
            for new_level in levels[level_index + 1:]:
                if self.is_end_of(new_level, backup_file):
                    self.write('{}    Moving {}/{} to {}'.format(
                        'DryRun: ' if self.dryrun else '',
                        level,
                        backup_file,
                        new_level
                    ), verbosity=1)
                    new_path = self.backup_levels[new_level]['path']
                    self.move(backup_file, file_extension, path, new_path)
                    moved = True
                    break
            if not moved:
                self.write('{}    Removing {}/{}'.format(
                    'DryRun: ' if self.dryrun else '',
                    level,
                    backup_file
                ), verbosity=1)
                self.delete(backup_file, file_extension, path)




class Command(BaseCommand):
    help = 'Backup file pruning tool'


    def add_arguments(self, parser):
        """Define command arguments"""
        # Positional arguments
        parser.add_argument(
            'backup_path',
            action='store',
            help='Path where backup files are stored',
        )
        parser.add_argument(
            'extension',
            action='store',
            dest='extensions',
            help='File extension of the backup files to prune '
                 '(more than one can be specified)',
            nargs='+',
        )

        # Optional arguments
        parser.add_argument(
            '--daily',
            action='store',
            default=14,
            dest='daily',
            help='Number of daily backups to keep (0 if no daily backups)',
        )
        parser.add_argument(
            '--weekly',
            action='store',
            default=6,
            dest='weekly',
            help='Number of weekly backups to keep (0 if no weekly backups)',
        )
        parser.add_argument(
            '--monthly',
            action='store',
            default=6,
            dest='monthly',
            help='Number of monthly backups to keep (0 if no monthly backups)',
        )
        parser.add_argument(
            '--yearly',
            action='store',
            default=6,
            dest='yearly',
            help='Number of yearly backups to keep (0 if no yearly backups)',
        )


    def handle(self, *args, **options):
        backup_path = options.pop('backup_path')
        extensions = options.pop('extensions')
        shears = Shears(backup_path, extensions, **options)
        try:
            shears.prune()
        except (ValueError,) as e:
            raise CommandError(e.msg)




if __name__ == '__main__':
    cmd = Command()
    cmd.run_from_argv(sys.argv)

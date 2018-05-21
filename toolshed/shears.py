from __future__ import print_function

from collections import OrderedDict
from datetime import datetime, timedelta

from .settings import *

import os


class Shears(object):
    def __init__(self, backup_path, file_extension):
        self.backup_path = backup_path
        self.file_extension = file_extension.strip().replace('.', '')
        self.backup_levels = OrderedDict()
        for level in ('daily', 'weekly', 'monthly', 'yearly'):
            try:
                days = BACKUP_LEVELS[level]
            except KeyError:
                continue
            self.backup_levels[level] = {
                'limit': days,
                'path': os.path.join(self.backup_path, level),
            }


    def delete(self, filename, path):
        """Delete existing backup file

        Arguments:
            filename {string} -- backup filename without the extension
                                 in the format YYYY-MM-DD
            path {string} -- Path to the backup file
        """
        filename = "{}.{}".format(filename, self.file_extension)
        os.remove(os.path.join(path, filename))


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


    def move(self, filename, path, new_path):
        """Move backup file to a new level

        Arguments:
            filename {string} -- backup filename without the extension
                                 in the format YYYY-MM-DD
            path {string} -- Path to the backup file
            new_path {string} -- Path where the backup file is going
        """
        filename = "{}.{}".format(filename, self.file_extension)
        src = os.path.join(path, filename)
        dest = os.path.join(new_path, filename)
        os.rename(src, dest)


    def prune(self):
        """Starting point to prune backups at all levels"""
        for level, details in self.backup_levels.items():
            self.prune_level(level, details['path'], details['limit'])


    def prune_level(self, level, path, limit):
        """Prune the files at one backup level

        Arguments:
            level {string} -- Backup level being processed
            path {object} -- OS path to the files in the backup level
            limit {integer} -- number of days worth of backups to keep
                               for this backup level
        """
        print("  pruning ./{}: {} max".format(level, limit))
        # read the valid backup files from `path`
        backup_files = []
        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):
                continue
            filename, extension = item.rsplit('.', 1)
            if extension != self.file_extension:
                continue
            if self.get_backup_date(filename) is not None:
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
                    print("    moving {}/{} to {}".format(
                        level, backup_file, new_level
                    ))
                    new_path = self.backup_levels[new_level]['path']
                    self.move(backup_file, path, new_path)
                    moved = True
                    break
            if not moved:
                print("    deleting {}/{}".format(level, backup_file))
                self.delete(backup_file, path)


    def strip_extension(self, filename):
        """Remove the file extension from the filename

        Arguments:
            filename {string} -- backup filename in the format YYYY-MM-DD.bak

        Returns:
            {string} -- `filename` without `self.file_extension` on the end
        """
        file_ext = '.{}'.format(self.file_extension)
        return filename.replace(file_ext, '')




if __name__ == '__main__':
    ### TODO: implement argparse and a proper call to shears.prune()
    shears = Shears('./', '.bak')
    shears.prune()

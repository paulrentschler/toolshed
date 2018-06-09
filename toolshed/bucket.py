#!/usr/bin/env python

from datetime import datetime
from subprocess import call, CalledProcessError, check_output, STDOUT

from toolshed.tool import BaseCommand, CommandError, Tool

import os
import shutil
import sys


class Bucket(Tool):
    def __init__(self, backup_path, **options):
        self.backup_path = backup_path
        self.base_path = backup_path
        self.database_type = options.get('database_type', 'mysql')
        self.db_host = options.get('db_host', 'localhost')
        self.db_pass = options.get('db_pass', None)
        self.db_user = options.get('db_user', None)
        self.dryrun = options.get('dryrun', False)
        self.encrypt_key = options.get('encrypt_key', None)
        self.file_group = options.get('file_group', None)
        self.file_owner = options.get('file_owner', None)
        self.today = datetime.now()
        self.verbosity = options.get('verbosity', 1)
        self.set_tables(
            options.get('tables_include', None),
            options.get('tables_exclude', None)
        )


    def backup(self):
        """Backup the databse"""
        self.write('{}Database ({}) backup for ({}) started on: {}\n'.format(
            'DryRun: ' if self.dryrun else '',
            self.database_type,
            self.db_host,
            self.today.strftime("%-m/%-d/%Y %H:%M"),
        ), verbosity=1)

        self.create_backup_folder()
        for database, tables in self.tables.items():
            if self._is_excluded(database):
                self.write('{}  Skipping database: {}'.format(
                    'DryRun: ' if self.dryrun else '',
                    database,
                ), verbosity=1)
                continue

            self.write('{}Backing up database: {}'.format(
                'DryRun: ' if self.dryrun else '',
                database,
            ), verbosity=1)
            for table in tables:
                if self._is_excluded(database, table):
                    self.write('{}     Skipping table: {}'.format(
                        'DryRun: ' if self.dryrun else '',
                        table,
                    ), verbosity=1)
                    continue

                self.write('{}   Backing up table: {}'.format(
                    'DryRun: ' if self.dryrun else '',
                    table,
                ), verbosity=2)

                # output the structure
                self.dump(database, table, structure=True, data=False)

                # output the data
                self.dump(database, table, structure=False, data=True)

        # collapse the folder of backup files into a single file
        self.collapse()

        # output the completion stats
        self.write('\n{}Backup finished on {}\n'.format(
            'DryRun: ' if self.dryrun else '',
            datetime.now().strftime('%-m/%-d/%Y %H:%M')
        ), verbosity=1)


    def collapse(self):
        """Collapse the folder of backup files into a single file

        Backup files are collapsed into a gzipped tar file or into a
        GnuPG encrypted file based on whether or not an encryption key
        is set.

        The resulting file can have it's ownership changed based on
        provided user and group values.
        """
        cmd = 'tar -cz *'
        filename = "{}.{}".format(
            self.today.strftime("%Y-%m-%d"),
            'bak' if self.encrypt_key else 'tar.gz',
        )
        filename = os.path.join(self.base_path, filename)
        success = True
        if self.encrypt_key:
            # encrypt the backup
            self.write('{}Encrypting backup files into: {}'.format(
                'DryRun: ' if self.dryrun else '',
                filename,
            ), verbosity=2)
            cmd += ' | gpg --output {} --encrypt --recipient {} > /dev/null'.format(  # NOQA
                filename,
                self.encrypt_key
            )
            if not self.dryrun:
                call(cmd, shell=True, cwd=self.backup_path)
        else:
            # tar the backup files
            self.write('{}Combine backup files into: {}'.format(
                'DryRun: ' if self.dryrun else '',
                filename
            ), verbosity=2)
            if not self.dryrun:
                try:
                    with open(filename, 'wb') as out_file:
                        call(cmd, shell=True, stdout=out_file, cwd=self.backup_path)  # NOQA
                except CalledProcessError:
                    success = False

        if success:
            # set the permissions and ownerships for files
            self.file_ownership_permissions([filename, ])

            # delete the original backup directory
            self.write('{}Delete the backup folder: {}'.format(
                'DryRun: ' if self.dryrun else '',
                self.backup_path,
            ), verbosity=2)
            if not self.dryrun:
                shutil.rmtree(self.backup_path)


    def create_backup_folder(self):
        """Create the backup folder to store the backup

        Creates a new date-based folder (format: YYYY-MM-DD) in the
        self.backup_path folder and returns it.

        Raises:
            FileExistsError -- If the backup folder for the current date
                               already exists, this exception is raised
        """
        today = datetime.now()
        current_folder = today.strftime("%Y-%m-%d")
        backup_path = os.path.join(self.base_path, current_folder)
        if os.path.exists(backup_path):
            raise FileExistsError('Backup path ({}) already exists!'.format(
                backup_path
            ))
        self.write('{}Create the backup folder: {}'.format(
            'DryRun: ' if self.dryrun else '',
            backup_path,
        ), verbosity=3)
        if not self.dryrun:
            os.makedirs(backup_path)
        self.backup_path = backup_path


    def dump(self, database, table, structure=False, data=False):
        """Database agnostic dump command for table structure and/or data

        Arguments:
            database {string} -- Database to dump
            table {string} -- Table to dump

        Keyword Arguments:
            structure {bool} -- Dump the database table structure
                                (default: {False})
            data {bool} -- Dump the database table data (default: {False})

        Raises:
            NotImplementedError -- raised if the database-specific dump
                                   command isn't implemented
        """
        if not structure and not data:
            raise ValueError('Must indicate if table structure or table '
                             'data or both are to be dumped')
        # create a path for the database files and ensure it exists
        path = os.path.join(self.backup_path, database)
        if not os.path.exists(path):
            self.write('{}       Create database path: {}'.format(
                'DryRun: ' if self.dryrun else '',
                path,
            ), verbosity=3)
            if not self.dryrun:
                os.makedirs(path)

        # determine the filename to use
        backup_content = ''
        if structure and not data:
            backup_content = 'structure'
        elif not structure and data:
            backup_content = 'data'
        filename = '{}_{}.{}.sql'.format(
            self.today.strftime('%Y-%m-%d'),
            table,
            backup_content
        )
        filename = os.path.join(path, filename)

        cmd = '_dump_{}'.format(self.database_type)
        try:
            self.write('{}       Writing {}'.format(
                'DryRun: ' if self.dryrun else '',
                backup_content,
            ), verbosity=3)
            if not self.dryrun:
                getattr(self, cmd)(filename, database, table, structure, data)
        except AttributeError:
            raise NotImplementedError(
                'Dump method ({}) for {} database is not '
                'implemented'.format(cmd, self.database_type)
            )


    def _dump_mysql(self, filename, database, table,
                    structure=False, data=False):
        """MySQL-specific dump command for table structure and/or data

        Arguments:
            filename {string} -- Filename for the dump file
            database {string} -- Database to dump
            table {string} -- Table to dump

        Keyword Arguments:
            structure {bool} -- Dump the database table structure
                                (default: {False})
            data {bool} -- Dump the database table data (default: {False})
        """
        cmd = ['mysqldump', '--skip-opt']
        if self.db_user is not None:
            cmd += ['--user', self.db_user]
        if self.db_pass is not None:
            cmd.append('--password=' + self.db_pass)
        if not structure:
            cmd.append('-t')
        if not data:
            cmd.append('-d')
        cmd += [database, table]
        with open(filename, 'wb') as dump_file:
            call(cmd, stdout=dump_file)


    def get_tables(self):
        """Database agnostic method to get all the databases/tables

        Returns:
            {dict} -- Dictionary of databases and tables where the database
                      names are the keys and the values are lists of tables
                      within each database

        Raises:
            NotImplementedError -- raised if the database-specific get
                                   tables command isn't implemented
        """
        cmd = '_get_tables_{}'.format(self.database_type)
        try:
            return getattr(self, cmd)()
        except AttributeError:
            raise NotImplementedError(
                'Get tables method ({}) for {} database is not '
                'implemented'.format(cmd, self.database_type)
            )


    def _get_tables_mysql(self):
        """MySQL-specific method to get all the databases/tables

        Returns:
            {dict} -- Dictionary of databases and tables where the database
                      names are the keys and the values are lists of tables
                      within each database
        """
        results = {}
        try:
            databases_raw = check_output(
                ['mysql', '-e', 'show databases'],
                stderr=STDOUT
            ).decode()
        except CalledProcessError:
            return results
        databases = databases_raw.split('\n')
        for database in databases[1:-1]:
            results[database] = []
            try:
                tables_raw = check_output(
                    ['mysql', database, '-e', 'show tables'],
                    stderr=STDOUT
                ).decode()
            except CalledProcessError:
                del results[database]
            else:
                tables = tables_raw.split('\n')
                for table in tables[1:-1]:
                    results[database].append(table)
        return results


    def _is_excluded(self, database, table=None):
        """Indicates if the database/table is excluded from the backup

        Arguments:
            database {string} -- The database name to check
            table {string} -- The table name to check

        Returns:
            bool -- Whether or not the database/table is to be
                    excluded from the backup
        """
        if database in self.tables_exclude.keys():
            if table is None:
                return not self.tables_exclude[database]
            else:
                return table in self.tables_exclude[database]


    def set_tables(self, tables_include, tables_exclude):
        """Set the databases/tables to backup

        Arguments:
            tables_include {list} -- List of `database.table` combinations
                                     to backup.  If not specified, all
                                     databases and tables are used.
            tables_exclude {list} -- List of `database.table` combinations
                                     to NOT backup.
        """
        self.tables = {}
        if tables_include:
            for entry in tables_include:
                database, table = entry.split('.', 1)
                if database not in self.tables.keys():
                    self.tables[database] = []
                self.tables[database].append(table)
        else:
            self.tables = self.get_tables()

        self.tables_exclude = {}
        if tables_exclude:
            for entry in tables_exclude:
                database, table = entry.split('.', 1)
                if database not in self.tables_exclude.keys():
                    self.tables_exclude[database] = []
                if table != '*':
                    self.tables_exclude[database].append(table)




class Command(BaseCommand):
    help = 'Database backup tool'


    def add_arguments(self, parser):
        """Define command arguments"""
        # Positional arguments
        parser.add_argument(
            'backup_path',
            action='store',
            help='Path to store backup files',
        )

        # Optional arguments
        parser.add_argument(
            '-e', '--encryptkey',
            action='store',
            default=None,
            dest='encrypt_key',
            help='Encryption key used to encrypt the backup files',
        )
        parser.add_argument(
            '--exclude',
            action='append',
            default=[],
            dest='tables_exclude',
            help='Database table to exclude from the backup in the format '
                 'database.table (can be used multiple times)',
        )
        parser.add_argument(
            '-g', '--group',
            action='store',
            default=None,
            dest='file_group',
            help='Unix group who should own the backup files',
        )
        parser.add_argument(
            '-h', '--host',
            action='store',
            default='localhost',
            dest='db_host',
            help='The database host to be backed up',
        )
        parser.add_argument(
            '--include',
            action='append',
            default=[],
            dest='tables_include',
            help='Database table to include in the backup in the format '
                 'database.table (database.* is valid) '
                 '(can be used multiple times)',
        )
        parser.add_argument(
            '-o', '--owner',
            action='store',
            default=None,
            dest='file_owner',
            help='Unix user who should own the backup files',
        )
        parser.add_argument(
            '-p', '--password',
            action='store',
            default=None,
            dest='db_pass',
            help="Used in conjunction with --user to specify "
                 "the user's password",
        )
        parser.add_argument(
            '-t', '--type',
            action='store',
            default='mysql',
            dest='database_type',
            help='Database type being backed up',
        )
        parser.add_argument(
            '-u', '--user',
            action='store',
            default=None,
            dest='db_user',
            help='Database user to connect as',
        )


    def handle(self, *args, **options):
        backup_path = options.pop('backup_path')
        bucket = Bucket(backup_path, **options)
        try:
            bucket.backup()
        except (FileExistsError, ValueError) as e:
            raise CommandError(e.msg)




if __name__ == '__main__':
    cmd = Command()
    cmd.run_from_argv(sys.argv)

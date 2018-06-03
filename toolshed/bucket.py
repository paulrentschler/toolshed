from datetime import datetime
from subprocess import call, CalledProcessError, check_output, STDOUT

from toolshed.settings import *
from toolshed.tool import Tool

import os
import shutil


class Bucket(Tool):
    def __init__(self, backup_path, **options):
        self.backup_path = backup_path
        self.base_path = backup_path
        self.database_type = options.get('database_type', 'mysql')
        self.db_host = options.get('db_host', 'localhost')
        self.db_pass = options.get('db_pass', None)
        self.db_user = options.get('db_user', None)
        self.encrypt_key = options.get('encrypt_key', None)
        self.file_group = options.get('file_group', None)
        self.file_user = options.get('file_user', None)
        self.today = datetime.now()
        self.verbosity = options.get('verbosity', 1)
        self.set_tables(
            options.get('tables_include', None),
            options.get('tables_exclude', None)
        )


    def backup(self):
        """Backup the databse"""
        self.write(
            'Database backup for ({}) started on: {}\n'.format(
                self.db_host,
                self.today.strftime("%-m/%-d/%Y %H:%M"),
            ),
            verbosity=1,
        )

        self.create_backup_folder()
        for database, tables in self.tables.items():
            self.write('Backing up database: {}'.format(database), verbosity=1)  # NOQA
            for table in tables:
                # output the structure
                self.dump(database, table, structure=True, data=False)

                # output the data
                self.dump(database, table, structure=False, data=True)

        # collapse the folder of backup files into a single file
        self.collapse()

        # output the completion stats
        self.write(
            '\nBackup finished on {}\n'.format(
                datetime.now().strftime('%-m/%-d/%Y %H:%M')
            ),
            verbosity=1
        )


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
            cmd += ' | gpg --output {} --encrypt --recipient {} > /dev/null'.format(  # NOQA
                filename,
                self.encrypt_key
            )
            call(cmd, shell=True, cwd=self.backup_path)
        else:
            # tar the backup files
            try:
                with open(filename, 'wb') as out_file:
                    call(cmd, shell=True, stdout=out_file, cwd=self.backup_path)  # NOQA
            except CalledProcessError:
                success = False

        if success:
            # fix the permissions on the backup file
            call(['chmod', '440', filename])
            if self.file_group is not None:
                call(['chgrp', self.file_group, filename])
            if self.file_user is not None:
                call(['chown', self.file_user, filename])

            # delete the original backup directory
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
            os.makedirs(path)

        # determine the filename extension to use
        extension = 'sql'
        if structure and not data:
            extension = 'structure.sql'
        elif not structure and data:
            extension = 'data.sql'
        filename = '{}_{}.{}'.format(
            self.today.strftime('%Y-%m-%d'),
            table,
            extension
        )
        filename = os.path.join(path, filename)

        cmd = '_dump_{}'.format(self.database_type)
        try:
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


    def set_tables(self, tables_include, tables_exclude):
        """Set the databases/tables to backup

        Arguments:
            tables_include {list} -- List of database.table combinations to
                                     backup.  If not None, only these tables
                                     are backed up.
            tables_exclude {list} -- List of database.table combinations to
                                     NOT backup.  If not None, will backup
                                     all databases and tables except the
                                     ones listed.
        """
        self.tables = {}
        if tables_include is not None:
            for entry in tables_include:
                database, table = entry.split('.', 1)
                if database not in self.tables.keys():
                    self.tables[database] = []
                self.tables[database].append(table)
        else:
            self.tables = self.get_tables()
            if tables_exclude is not None:
                for entry in tables_exclude:
                    database, table = entry.split('.', 1)
                    if table == '*':
                        try:
                            del self.tables[database]
                        except KeyError:
                            pass
                    else:
                        try:
                            self.tables[database].remove(table)
                        except (KeyError, ValueError):
                            pass




if __name__ == '__main__':
    ### TODO: implement argparse and a proper call to bucket.backup()
    bucket = Bucket('./')
    bucket.backup()

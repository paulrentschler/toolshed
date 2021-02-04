from datetime import datetime
from subprocess import call

from toolshed.bucket import Bucket

import os
import shutil
import unittest
import uuid


class TestBucket(unittest.TestCase):

    def create_dir(self, suffix=''):
        """Create a temporary directory structure to use for the tests

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


    def test_backup_all(self):
        """Test backing up the entire database"""
        tmp_path = self.create_dir('all')
        bucket = Bucket(tmp_path, verbosity=0)
        bucket.backup()
        backup_date = datetime.now().strftime("%Y-%m-%d")
        backup_dir = os.path.join(tmp_path, backup_date)
        os.makedirs(backup_dir)
        call(
            ['tar', '-zxmf', os.path.join('..', backup_date + '.tar.gz')],
            cwd=backup_dir
        )
        database_dirs = os.listdir(backup_dir)
        self.assertTrue(
            len(database_dirs) >= 2,
            msg='Backup does not include at least two databases directories'
        )
        self.assertTrue(
            'information_schema' in database_dirs,
            msg='"information_schema" database not backed up'
        )
        self.assertTrue(
            'mysql' in database_dirs,
            msg='"mysql" database not backed up'
        )
        table_dirs = os.listdir(os.path.join(backup_dir, 'information_schema'))  # NOQA
        self.assertListEqual(
            sorted(table_dirs),
            [
                '{}_CHARACTER_SETS.data.sql'.format(backup_date),
                '{}_CHARACTER_SETS.structure.sql'.format(backup_date),
                '{}_COLLATIONS.data.sql'.format(backup_date),
                '{}_COLLATIONS.structure.sql'.format(backup_date),
                '{}_COLLATION_CHARACTER_SET_APPLICABILITY.data.sql'.format(backup_date),  # NOQA
                '{}_COLLATION_CHARACTER_SET_APPLICABILITY.structure.sql'.format(backup_date),  # NOQA
                '{}_COLUMNS.data.sql'.format(backup_date),
                '{}_COLUMNS.structure.sql'.format(backup_date),
                '{}_COLUMN_PRIVILEGES.data.sql'.format(backup_date),
                '{}_COLUMN_PRIVILEGES.structure.sql'.format(backup_date),
                '{}_ENGINES.data.sql'.format(backup_date),
                '{}_ENGINES.structure.sql'.format(backup_date),
                '{}_EVENTS.data.sql'.format(backup_date),
                '{}_EVENTS.structure.sql'.format(backup_date),
                '{}_FILES.data.sql'.format(backup_date),
                '{}_FILES.structure.sql'.format(backup_date),
                '{}_GLOBAL_STATUS.data.sql'.format(backup_date),
                '{}_GLOBAL_STATUS.structure.sql'.format(backup_date),
                '{}_GLOBAL_VARIABLES.data.sql'.format(backup_date),
                '{}_GLOBAL_VARIABLES.structure.sql'.format(backup_date),
                '{}_INNODB_BUFFER_PAGE.data.sql'.format(backup_date),
                '{}_INNODB_BUFFER_PAGE.structure.sql'.format(backup_date),
                '{}_INNODB_BUFFER_PAGE_LRU.data.sql'.format(backup_date),
                '{}_INNODB_BUFFER_PAGE_LRU.structure.sql'.format(backup_date),
                '{}_INNODB_BUFFER_POOL_STATS.data.sql'.format(backup_date),
                '{}_INNODB_BUFFER_POOL_STATS.structure.sql'.format(backup_date),  # NOQA
                '{}_INNODB_CMP.data.sql'.format(backup_date),
                '{}_INNODB_CMP.structure.sql'.format(backup_date),
                '{}_INNODB_CMPMEM.data.sql'.format(backup_date),
                '{}_INNODB_CMPMEM.structure.sql'.format(backup_date),
                '{}_INNODB_CMPMEM_RESET.data.sql'.format(backup_date),
                '{}_INNODB_CMPMEM_RESET.structure.sql'.format(backup_date),
                '{}_INNODB_CMP_RESET.data.sql'.format(backup_date),
                '{}_INNODB_CMP_RESET.structure.sql'.format(backup_date),
                '{}_INNODB_LOCKS.data.sql'.format(backup_date),
                '{}_INNODB_LOCKS.structure.sql'.format(backup_date),
                '{}_INNODB_LOCK_WAITS.data.sql'.format(backup_date),
                '{}_INNODB_LOCK_WAITS.structure.sql'.format(backup_date),
                '{}_INNODB_TRX.data.sql'.format(backup_date),
                '{}_INNODB_TRX.structure.sql'.format(backup_date),
                '{}_KEY_COLUMN_USAGE.data.sql'.format(backup_date),
                '{}_KEY_COLUMN_USAGE.structure.sql'.format(backup_date),
                '{}_PARAMETERS.data.sql'.format(backup_date),
                '{}_PARAMETERS.structure.sql'.format(backup_date),
                '{}_PARTITIONS.data.sql'.format(backup_date),
                '{}_PARTITIONS.structure.sql'.format(backup_date),
                '{}_PLUGINS.data.sql'.format(backup_date),
                '{}_PLUGINS.structure.sql'.format(backup_date),
                '{}_PROCESSLIST.data.sql'.format(backup_date),
                '{}_PROCESSLIST.structure.sql'.format(backup_date),
                '{}_PROFILING.data.sql'.format(backup_date),
                '{}_PROFILING.structure.sql'.format(backup_date),
                '{}_REFERENTIAL_CONSTRAINTS.data.sql'.format(backup_date),
                '{}_REFERENTIAL_CONSTRAINTS.structure.sql'.format(backup_date),  # NOQA
                '{}_ROUTINES.data.sql'.format(backup_date),
                '{}_ROUTINES.structure.sql'.format(backup_date),
                '{}_SCHEMATA.data.sql'.format(backup_date),
                '{}_SCHEMATA.structure.sql'.format(backup_date),
                '{}_SCHEMA_PRIVILEGES.data.sql'.format(backup_date),
                '{}_SCHEMA_PRIVILEGES.structure.sql'.format(backup_date),
                '{}_SESSION_STATUS.data.sql'.format(backup_date),
                '{}_SESSION_STATUS.structure.sql'.format(backup_date),
                '{}_SESSION_VARIABLES.data.sql'.format(backup_date),
                '{}_SESSION_VARIABLES.structure.sql'.format(backup_date),
                '{}_STATISTICS.data.sql'.format(backup_date),
                '{}_STATISTICS.structure.sql'.format(backup_date),
                '{}_TABLES.data.sql'.format(backup_date),
                '{}_TABLES.structure.sql'.format(backup_date),
                '{}_TABLESPACES.data.sql'.format(backup_date),
                '{}_TABLESPACES.structure.sql'.format(backup_date),
                '{}_TABLE_CONSTRAINTS.data.sql'.format(backup_date),
                '{}_TABLE_CONSTRAINTS.structure.sql'.format(backup_date),
                '{}_TABLE_PRIVILEGES.data.sql'.format(backup_date),
                '{}_TABLE_PRIVILEGES.structure.sql'.format(backup_date),
                '{}_TRIGGERS.data.sql'.format(backup_date),
                '{}_TRIGGERS.structure.sql'.format(backup_date),
                '{}_USER_PRIVILEGES.data.sql'.format(backup_date),
                '{}_USER_PRIVILEGES.structure.sql'.format(backup_date),
                '{}_VIEWS.data.sql'.format(backup_date),
                '{}_VIEWS.structure.sql'.format(backup_date),
            ],
            msg='Backed up "information_schema" tables do not match expected'
        )
        table_dirs = os.listdir(os.path.join(backup_dir, 'mysql'))
        self.assertListEqual(
            sorted(table_dirs),
            [
                '{}_columns_priv.data.sql'.format(backup_date),
                '{}_columns_priv.structure.sql'.format(backup_date),
                '{}_db.data.sql'.format(backup_date),
                '{}_db.structure.sql'.format(backup_date),
                '{}_event.data.sql'.format(backup_date),
                '{}_event.structure.sql'.format(backup_date),
                '{}_func.data.sql'.format(backup_date),
                '{}_func.structure.sql'.format(backup_date),
                '{}_general_log.data.sql'.format(backup_date),
                '{}_general_log.structure.sql'.format(backup_date),
                '{}_help_category.data.sql'.format(backup_date),
                '{}_help_category.structure.sql'.format(backup_date),
                '{}_help_keyword.data.sql'.format(backup_date),
                '{}_help_keyword.structure.sql'.format(backup_date),
                '{}_help_relation.data.sql'.format(backup_date),
                '{}_help_relation.structure.sql'.format(backup_date),
                '{}_help_topic.data.sql'.format(backup_date),
                '{}_help_topic.structure.sql'.format(backup_date),
                '{}_host.data.sql'.format(backup_date),
                '{}_host.structure.sql'.format(backup_date),
                '{}_ndb_binlog_index.data.sql'.format(backup_date),
                '{}_ndb_binlog_index.structure.sql'.format(backup_date),
                '{}_plugin.data.sql'.format(backup_date),
                '{}_plugin.structure.sql'.format(backup_date),
                '{}_proc.data.sql'.format(backup_date),
                '{}_proc.structure.sql'.format(backup_date),
                '{}_procs_priv.data.sql'.format(backup_date),
                '{}_procs_priv.structure.sql'.format(backup_date),
                '{}_proxies_priv.data.sql'.format(backup_date),
                '{}_proxies_priv.structure.sql'.format(backup_date),
                '{}_servers.data.sql'.format(backup_date),
                '{}_servers.structure.sql'.format(backup_date),
                '{}_slow_log.data.sql'.format(backup_date),
                '{}_slow_log.structure.sql'.format(backup_date),
                '{}_tables_priv.data.sql'.format(backup_date),
                '{}_tables_priv.structure.sql'.format(backup_date),
                '{}_time_zone.data.sql'.format(backup_date),
                '{}_time_zone.structure.sql'.format(backup_date),
                '{}_time_zone_leap_second.data.sql'.format(backup_date),
                '{}_time_zone_leap_second.structure.sql'.format(backup_date),
                '{}_time_zone_name.data.sql'.format(backup_date),
                '{}_time_zone_name.structure.sql'.format(backup_date),
                '{}_time_zone_transition.data.sql'.format(backup_date),
                '{}_time_zone_transition.structure.sql'.format(backup_date),
                '{}_time_zone_transition_type.data.sql'.format(backup_date),
                '{}_time_zone_transition_type.structure.sql'.format(backup_date),  # NOQA
                '{}_user.data.sql'.format(backup_date),
                '{}_user.structure.sql'.format(backup_date),
            ],
            msg='Backed up "mysql" tables do not match expected'
        )
        self.remove_dir(tmp_path)


    def test_backup_exclude(self):
        """Test backing up the entire database with some exclusions"""
        tmp_path = self.create_dir('exclude')
        bucket = Bucket(
            tmp_path,
            tables_exclude=[
                'information_schema.*',
                'mysql.event',
                'mysql.func',
                'mysql.general_log',
                'mysql.help_category',
                'mysql.help_keyword',
                'mysql.help_relation',
                'mysql.help_topic',
                'mysql.ndb_binlog_index',
                'mysql.plugin',
                'mysql.proc',
                'mysql.procs_priv',
                'mysql.proxies_priv',
                'mysql.slow_log',
                'mysql.time_zone',
                'mysql.time_zone_leap_second',
                'mysql.time_zone_name',
                'mysql.time_zone_transition',
                'mysql.time_zone_transition_type',
            ],
            verbosity=0
        )
        bucket.backup()
        backup_date = datetime.now().strftime("%Y-%m-%d")
        backup_dir = os.path.join(tmp_path, backup_date)
        os.makedirs(backup_dir)
        call(
            ['tar', '-zxmf', os.path.join('..', backup_date + '.tar.gz')],
            cwd=backup_dir
        )
        database_dirs = os.listdir(backup_dir)
        self.assertTrue(
            len(database_dirs) >= 1,
            msg='Backup does not include at least one database directory'
        )
        self.assertFalse(
            'information_schema' in database_dirs,
            msg='"information_schema" database not excluded from backup'
        )
        self.assertTrue(
            'mysql' in database_dirs,
            msg='"mysql" database not backed up'
        )
        table_dirs = os.listdir(os.path.join(backup_dir, 'mysql'))
        self.assertListEqual(
            sorted(table_dirs),
            [
                '{}_columns_priv.data.sql'.format(backup_date),
                '{}_columns_priv.structure.sql'.format(backup_date),
                '{}_db.data.sql'.format(backup_date),
                '{}_db.structure.sql'.format(backup_date),
                '{}_host.data.sql'.format(backup_date),
                '{}_host.structure.sql'.format(backup_date),
                '{}_servers.data.sql'.format(backup_date),
                '{}_servers.structure.sql'.format(backup_date),
                '{}_tables_priv.data.sql'.format(backup_date),
                '{}_tables_priv.structure.sql'.format(backup_date),
                '{}_user.data.sql'.format(backup_date),
                '{}_user.structure.sql'.format(backup_date),
            ],
            msg='Backed up "mysql" tables do not match expected'
        )
        self.remove_dir(tmp_path)


    def test_backup_include(self):
        """Test backing up only selected tables"""
        tmp_path = self.create_dir('include')
        bucket = Bucket(
            tmp_path,
            tables_include=[
                'mysql.db',
                'mysql.host',
                'mysql.user',
            ],
            verbosity=0
        )
        bucket.backup()
        backup_date = datetime.now().strftime("%Y-%m-%d")
        backup_dir = os.path.join(tmp_path, backup_date)
        os.makedirs(backup_dir)
        call(
            ['tar', '-zxmf', os.path.join('..', backup_date + '.tar.gz')],
            cwd=backup_dir
        )
        database_dirs = os.listdir(backup_dir)
        self.assertTrue(
            len(database_dirs) == 1,
            msg='Backup does not include exactly one database directory'
        )
        self.assertFalse(
            'information_schema' in database_dirs,
            msg='"information_schema" database not excluded from backup'
        )
        self.assertTrue(
            'mysql' in database_dirs,
            msg='"mysql" database not backed up'
        )
        table_dirs = os.listdir(os.path.join(backup_dir, 'mysql'))
        self.assertListEqual(
            sorted(table_dirs),
            [
                '{}_db.data.sql'.format(backup_date),
                '{}_db.structure.sql'.format(backup_date),
                '{}_host.data.sql'.format(backup_date),
                '{}_host.structure.sql'.format(backup_date),
                '{}_user.data.sql'.format(backup_date),
                '{}_user.structure.sql'.format(backup_date),
            ],
            msg='Backed up "mysql" tables do not match expected'
        )
        self.remove_dir(tmp_path)


    def test_settables_all(self):
        """Ensure Bucket.set_tables() finds all the tables by default"""
        bucket = Bucket('./')
        bucket.set_tables(None, None)
        self.assertTrue(
            len(bucket.tables_exclude.keys()) == 0,
            msg='Excluded tables list is not empty'
        )
        self.assertTrue(
            len(bucket.tables.keys()) >= 2,
            msg='Tables list does not include at least two databases'
        )
        self.assertTrue(
            'information_schema' in bucket.tables.keys(),
            msg='"information_schema" database not included'
        )
        self.assertTrue(
            'mysql' in bucket.tables.keys(),
            msg='"mysql" database not included'
        )
        self.assertListEqual(
            sorted(bucket.tables['information_schema']),
            [
                'CHARACTER_SETS',
                'COLLATIONS',
                'COLLATION_CHARACTER_SET_APPLICABILITY',
                'COLUMNS',
                'COLUMN_PRIVILEGES',
                'ENGINES',
                'EVENTS',
                'FILES',
                'GLOBAL_STATUS',
                'GLOBAL_VARIABLES',
                'INNODB_BUFFER_PAGE',
                'INNODB_BUFFER_PAGE_LRU',
                'INNODB_BUFFER_POOL_STATS',
                'INNODB_CMP',
                'INNODB_CMPMEM',
                'INNODB_CMPMEM_RESET',
                'INNODB_CMP_RESET',
                'INNODB_LOCKS',
                'INNODB_LOCK_WAITS',
                'INNODB_TRX',
                'KEY_COLUMN_USAGE',
                'PARAMETERS',
                'PARTITIONS',
                'PLUGINS',
                'PROCESSLIST',
                'PROFILING',
                'REFERENTIAL_CONSTRAINTS',
                'ROUTINES',
                'SCHEMATA',
                'SCHEMA_PRIVILEGES',
                'SESSION_STATUS',
                'SESSION_VARIABLES',
                'STATISTICS',
                'TABLES',
                'TABLESPACES',
                'TABLE_CONSTRAINTS',
                'TABLE_PRIVILEGES',
                'TRIGGERS',
                'USER_PRIVILEGES',
                'VIEWS',
            ],
            msg='"information_schema" tables do not match expected'
        )
        self.assertListEqual(
            sorted(bucket.tables['mysql']),
            [
                'columns_priv',
                'db',
                'event',
                'func',
                'general_log',
                'help_category',
                'help_keyword',
                'help_relation',
                'help_topic',
                'host',
                'ndb_binlog_index',
                'plugin',
                'proc',
                'procs_priv',
                'proxies_priv',
                'servers',
                'slow_log',
                'tables_priv',
                'time_zone',
                'time_zone_leap_second',
                'time_zone_name',
                'time_zone_transition',
                'time_zone_transition_type',
                'user',
            ],
            msg='"mysql" tables do not match expected'
        )


    def test_settables_exclude(self):
        """Ensure Bucket.set_tables() excludes specified tables"""
        bucket = Bucket('./')
        bucket.set_tables(None, ['information_schema.*', 'mysql.slow_log'])
        self.assertTrue(
            len(bucket.tables_exclude.keys()) == 2,
            msg='Excluded tables list does not include two databases'
        )
        self.assertTrue(
            'information_schema' in bucket.tables_exclude.keys(),
            msg='"information_schema" database is not in excluded list'
        )
        self.assertListEqual(
            bucket.tables_exclude['information_schema'],
            [],
            msg='"information_schema" database is not completely excluded'
        )
        self.assertTrue(
            'mysql' in bucket.tables_exclude.keys(),
            msg='"mysql" database is not in excluded list'
        )
        self.assertListEqual(
            bucket.tables_exclude['mysql'],
            ['slow_log', ],
            msg='"slow_log" table is not the only table excluded'
        )
        self.assertTrue(
            len(bucket.tables.keys()) >= 2,
            msg='Tables list does not include at least two databasees'
        )
        self.assertTrue(
            'information_schema' in bucket.tables.keys(),
            msg='"information_schema" database is not included'
        )
        self.assertTrue(
            'mysql' in bucket.tables.keys(),
            msg='"mysql" database is not included'
        )
        self.assertListEqual(
            sorted(bucket.tables['mysql']),
            [
                'columns_priv',
                'db',
                'event',
                'func',
                'general_log',
                'help_category',
                'help_keyword',
                'help_relation',
                'help_topic',
                'host',
                'ndb_binlog_index',
                'plugin',
                'proc',
                'procs_priv',
                'proxies_priv',
                'servers',
                'slow_log',
                'tables_priv',
                'time_zone',
                'time_zone_leap_second',
                'time_zone_name',
                'time_zone_transition',
                'time_zone_transition_type',
                'user',
            ],
            msg='"mysql" tables do not match expected'
        )


    def test_settables_include(self):
        """Ensure Bucket.set_tables() only includes specified tables"""
        bucket = Bucket('./')
        bucket.set_tables(['mysql.db', 'mysql.host', 'mysql.user'], None)
        self.assertTrue(
            len(bucket.tables_exclude.keys()) == 0,
            msg='Excluded tables list is not'
        )
        self.assertTrue(
            len(bucket.tables.keys()) == 1,
            msg='Tables list does not include exactly one database'
        )
        self.assertFalse(
            'information_schema' in bucket.tables.keys(),
            msg='"information_schema" database is not excluded'
        )
        self.assertTrue(
            'mysql' in bucket.tables.keys(),
            msg='"mysql" database not included'
        )
        self.assertListEqual(
            sorted(bucket.tables['mysql']),
            [
                'db',
                'host',
                'user',
            ],
            msg='"mysql" tables do not match expected'
        )




if __name__ == '__main__':
    unittest.main()

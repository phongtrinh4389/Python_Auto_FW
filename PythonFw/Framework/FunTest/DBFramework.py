__author__ = 'david.hewitt'
from functools import partial

import pypyodbc
import os
import FunTest.Exceptions as Ex
import time
from FunTest.AddFolder import run_util
from subprocess import call

from FunTest.TableSchema import TableSchema


class DBTester(object):
    """Database access class providing the basic requirements in a simple interface"""
    conn_string_base = 'Driver={SQL Server};' + \
        'Server=%s;' + \
        'Database=%s;' + \
        'Trusted_Connection=yes;'

    def __init__(self, default_key, database_list, db_server, remote=None):
        self.default_key = default_key
        self.db_names = database_list
        self.db_server = db_server
        self.remote = remote

    def generate_connection_string(self, db=None):
        if db:
            db_key = db
        else:
            db_key = self.default_key
        return self.conn_string_base % (self.db_server, self.db_names[db_key])

    def select_query(self, db, query):
        connection_string = self.generate_connection_string(db)
        for i in range(0, 5):
            try:
                with pypyodbc.connect(connection_string, autocommit=True) as conn:
                    with conn.cursor() as cursor:
                        rows = cursor.execute(query).fetchall()
                cursor.close()
                return rows
            except Exception:
                time.sleep(5)
        return None

    def execute_query(self, db, query):
        connection_string = self.generate_connection_string(db)
        for i in range(0, 5):
            try:
                with pypyodbc.connect(connection_string, autocommit=True) as conn:
                    with conn.cursor() as cursor:
                        status = cursor.execute(query)
                cursor.close()
                return status
            except Exception:
                time.sleep(5)

    @staticmethod
    def execute_base(connection_string, query, function, params):
        """Run a query against the selected database - no transaction to allow drop database etc"""
        with pypyodbc.connect(connection_string, autocommit=True) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if function is not None:
                    return function(cursor)
                else:
                    return None

    def execute(self, query, function, params, db):
        return self.execute_base(self.generate_connection_string(db), query, function, params)

    def execute_from_master(self, query, function=None, params=None):
        conn_string = self.conn_string_base % (self.db_server, 'test')
        return self.execute_base(conn_string, query, function, params)

    @staticmethod
    def get_snapshot_db_name(snapshot, db):
        if snapshot is None:
            snapshot = db + '_initial'
        return snapshot

    def __restore(self, db_name, snapshot=None):
        """Restore the database to a snapshot"""
        db = self.db_names[db_name]
        # query = "restore database %s from database_snapshot = '%s'" % (db, self.get_snapshot_db_name(snapshot, db))
        query = """
        ALTER DATABASE [%s] SET SINGLE_USER WITH ROLLBACK IMMEDIATE ;
        restore database [%s] from database_snapshot = '%s'
        """ % (db, db, self.get_snapshot_db_name(snapshot, db))
        self.execute_from_master(query)
        # Set back to multi user mode
        query = "ALTER DATABASE [%s] SET MULTI_USER" %(db)
        self.execute_from_master(query)

    def restore(self):
        for db_name in iter(self.db_names.keys()):
            self.__restore(db_name)

    def check_snapshot(self, db_name, snapshot=None):
        db = self.db_names[db_name]
        snapshot = self.get_snapshot_db_name(snapshot, db)
        query = """
        select COUNT(*)
        from sys.databases m
        inner join sys.databases s
        on m.database_id = s.source_database_id
        where  m.name = ? and s.name = ?"""
        n = self.execute_from_master(query, lambda c: DBTester.get_column_from_cursor(c, 0), [db, snapshot])
        return n == 1

    @staticmethod
    def get_column_from_cursor(cursor, column_name):
        row = cursor.fetchone()
        if not row:
            raise Ex.TooFewRowsError("Expected at least a single match")
        return row[column_name]

    def get_file_group(self, db):
        query = 'SELECT  name  FROM sys.master_files  where type = 0 and UPPER(DB_NAME(database_id))= ?'
        return self.execute_from_master(query, lambda c: DBTester.get_column_from_cursor(c, 0), [db.upper()])

    def __create_snapshot(self, db_name, snapshot_dir, snapshot=None):
        if not os.path.exists(snapshot_dir):
            os.makedirs(snapshot_dir)

        db = self.db_names[db_name]
        snapshot = self.get_snapshot_db_name(snapshot, db)
        file_path = os.path.join(snapshot_dir, snapshot + ".ss")
        file_group = self.get_file_group(db)
        query = """
        create database %s
        on (
            Name = %s,
            FILENAME ='%s'
        ) as snapshot of %s""" % (snapshot, file_group, file_path, db)
        self.execute_from_master(query)

    def create_snapshot(self, snapshot_dir, snapshot=None):
        for db_name in iter(self.db_names.keys()):
            self.__create_snapshot(db_name, snapshot_dir, snapshot)

    def __remove_snapshot(self, db_name, snapshot=None):
        db = self.db_names[db_name]
        query = "drop database %s" % self.get_snapshot_db_name(snapshot, db)
        self.execute_from_master(query)

    def remove_snapshot(self, snapshot=None):
        for db_name in iter(self.db_names.keys()):
            self.__remove_snapshot(db_name, snapshot)

    def __refresh_snapshot(self, db_name, snapshot_dir, snapshot=None):
        if self.check_snapshot(db_name, snapshot):
            self.__restore(db_name, snapshot)
            self.__remove_snapshot(db_name, snapshot)
        self.__create_snapshot(db_name, snapshot_dir, snapshot)

    def refresh_snapshots(self, root_dir):
        for db_name in iter(self.db_names.keys()):
            self.__refresh_snapshot(db_name, root_dir, None)

    @staticmethod
    def compare_values(cursor, values):
        row = cursor.fetchone()
        if not row:
            raise Ex.TooFewRowsError("Expected at least a single match")
        result = dict([(v, (row[v.lower()] == values[v], row[v.lower()], values[v])) for v in values.keys()])
        if cursor.fetchone():
            raise Ex.TooManyRowsError("Expected only a single match")
        return result

    @staticmethod
    def capture_schema(cursor):
        row = cursor.fetchone()
        if not row:
            raise Ex.TooFewRowsError("Expected at least a single match")
        result = {}
        while row:
            result[row['column_name']] = None
            row = cursor.fetchone()
        return result

    def check_values(self, table, keys, values, db=None):
        projection = ','.join(iter(values.keys()))
        selection = ' = ? and '. join(iter(keys.keys())) + ' = ? '
        query = 'SELECT %s FROM %s WHERE %s' % (projection, table, selection)
        params = list(keys.values())
        function = partial(DBTester.compare_values, values=values)
        result = self.execute(query, function, params, db)
        return result

    def report_check(self, table, keys, values, db=None):
        res = self.check_values(table, keys, values, db)
        result = [x for x in res if not res[x][0]]
        if result:
            raise Ex.DbCheckFailedException(result)

    def create_comparison_template(self, table, template_path, name, db=None):
        query = 'SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?'
        params = [table]
        function = DBTester.capture_schema
        result = self.execute(query, function, params, db)
        TableSchema.write_template(table, result, template_path, name)

    def clear_connections(self):
        pass

    def reset_iis(self):
        if self.remote:
            os.system('iisreset ' + self.remote)
        else:
            run_util('iisreset')
__author__ = 'david.hewitt'
from FunTest.CodeGenerator import write_template, format_transform_list
import datetime


class TableSchema(object):
    """Base class for table schema transforms"""
    def __init__(self, table_name, key_db_column_names, transform, db=None):
        self.table_name = table_name
        self.transform = transform
        self.key_db_column_names = key_db_column_names
        self.db = db

    def construct_value(self, row, key):
        value_source = self.transform[key]
        if isinstance(value_source, str):
            return row.data[value_source.lower()]
        else:
            return value_source(row)

    def create_comparison(self, row):
        key_values = [(x, self.construct_value(row, x)) for x in self.key_db_column_names]
        values = [(x, self.construct_value(row, x)) for x in iter(self.transform.keys())]
        result = (self.table_name, dict(key_values), dict(values), self.db)
        return result

    @staticmethod
    def write_template(table_name, transform, output_path, output_name):
        columns = [x for x in transform]  # keys
        column_string = format_transform_list(columns)

        replacement_dictionary = {'name': output_name, 'transforms': column_string, 'table_name': table_name}
        write_template('DbTableSchema',  output_path, output_name, replacement_dictionary)
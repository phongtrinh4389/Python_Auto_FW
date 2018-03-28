__author__ = 'david.hewitt'
from FunTest.Row import Row
import FunTest.Exceptions as Ex


class DataSet(object):
    """representation of a set of test data to use in a web test"""
    def __init__(self, name):
        self.name = name
        self.indexes = None
        self.descriptions = None
        self.not_striped_columns = None
        self.columns = None
        self.rows = {}

    @staticmethod
    def adjust_fields(columns):
        """Strips off the 1st character iff * | #
           '*' => column is index
           '#' means it is a description column
           note that these are mutually exclusive"""
        indexes = []
        descriptions = []
        titles = []
        not_striped_columns = []

        for s in columns:
            # column names are kept lower case for
            # case insensitive comparison
            s = s.strip().lower()

            if s.startswith('*'):
                title = s[1:]
                titles.append(title)
                indexes.append(title)

            elif s.startswith('#'):
                title = s[1:]
                titles.append(title)
                descriptions.append(title)

            elif s.startswith('@'):
                title = s[1:]
                titles.append(title)
                not_striped_columns.append(title)

            else:
                titles.append(s)

        return indexes, descriptions, not_striped_columns, titles

    def append(self, row_data):
        if self.indexes is None:
            self.indexes, self.descriptions, self.not_striped_columns, self.columns = DataSet.adjust_fields(row_data)
        else:
            list = [x for x in row_data]
            new_row = Row(self,list )
            self.rows[new_row.get_string_index()] = new_row

    def fetch(self, key):
        if key in self.rows:
            return self.rows[key]
        else:
            raise Ex.KeyMissingException(key)

    def get_rows(self):
        return iter(self.rows.values())


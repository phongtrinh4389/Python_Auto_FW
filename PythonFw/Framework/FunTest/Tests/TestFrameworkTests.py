__author__ = 'david.hewitt'
import unittest
from io import StringIO  # note python 3 uses io.StringIO not StringIO.StringIO

from FunTest.Repository import Repo
from FunTest.Row import Row


class RepoTest(unittest.TestCase):
    """Test the repo implementation - so we know how it works"""
    def setUp(self):
        self.target = Repo('path')

    def test_form_path(self):
        """is the form path initialised correctly"""
        file_path = self.target.form_repo.root_path
        self.assertIn('Form', file_path)

    def test_data_path(self):
        """is the data path initialised correctly"""
        file_path = self.target.data_repo.root_path
        self.assertIn('Data', file_path)

    def test_form_repo(self):
        """Check the form loads some JSON object
           Does not validate that it IS a form object(!)"""
        name = 'the_form'
        self.target.get_file = lambda x: StringIO('{"PROP" : "VALUE"}')  # replace the file load with a string load
        form = self.target.get_form(name)
        self.assertEquals(name, form.name)
        self.assertIn('PROP', form.config)

    def test_data_repo(self):
        """Check it loads a csv list
            Does not need to validate contents
            as they are just a dictionary"""
        name = 'the_data'
        self.target.get_file = lambda x: StringIO('"*Name","Age"\n"Fred",22\n')  # replace the file load
        data = self.target.get_data_set(name)
        self.assertEquals(name, data.name)
        self.assertEquals(1, len(data.rows))
        self.assertEquals(2, len(data.columns))
        key = Row.form_key_string('Fred')
        row = data.fetch(key)
        self.assertIsNotNone(row)
        self.assertEquals('Fred', row.data['Name'])

# run tests
if __name__ == '__main__':
    unittest.main(warnings='ignore')
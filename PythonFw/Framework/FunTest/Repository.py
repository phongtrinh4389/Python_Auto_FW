__author__ = 'david.hewitt'
from FunTest.AddFolder import get_path_root
import codecs
from FunTest.Factories import FormFactory, DataFactory
import os
import FunTest.Exceptions as Ex
from FunTest.CodeGenerator import write_template


class Repo(object):
    """maps object requests to the object"""
    def __init__(self, test_repo):
        self.root = test_repo
        form_root = os.path.join(self.root, 'Form')
        data_root = os.path.join(self.root, 'Data')
        self.form_repo = FormFactory(form_root, self)
        self.data_repo = DataFactory(data_root, self)
        # note this lambda get replaced when testing with strings instead of files
        self.get_file = lambda file_path: Repo.skip_bom(file_path)

    @staticmethod
    def create_directory(file_path, subdirectory=None, create_module=False):
        if subdirectory is None:
            full_path = file_path
        else:
            full_path = os.path.join(file_path, subdirectory)
        os.makedirs(full_path)
        if create_module:
            with open(os.path.join(full_path, '__init__.py'), 'w') as file:
                file.write("__author__ = 'generated'\n")

    @staticmethod
    def build_repo(name, url, default_db, db_list, db_server, root_dir=None):
        """creates a module called <name>Repo
           in the same directory as the root
           of the test application"""
        if root_dir is None:
            root_dir = get_path_root()

        if not url.endswith('/'):
            url += '/'

        actual_dir = os.path.join(root_dir, name + 'Repo')

        if os.path.exists(actual_dir):
            raise Ex.RepoExistsException(name, actual_dir)

        Repo.create_directory(actual_dir, None, True)
        Repo.create_directory(actual_dir, 'Data')
        Repo.create_directory(actual_dir, 'Form')
        Repo.create_directory(actual_dir, 'Plan', True)
        Repo.create_directory(actual_dir, 'Sequences', True)
        Repo.create_directory(actual_dir, 'SchemaMappers', True)
        Repo.create_directory(actual_dir, 'HtmlTableMappers', True)

        file_name = '%sTestConfig' % name
        data = {'name': name, 'url': url, 'default': default_db, 'list': db_list.__repr__(),'db_server': db_server}
        write_template('Config', actual_dir, file_name, data)


    @staticmethod
    def get_bom_encoding(raw):
        for enc, bom_values in \
                ('utf-8-sig', (codecs.BOM_UTF8,)),\
                ('utf-16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),\
                ('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
            if any(raw.startswith(bom) for bom in bom_values):
                return enc

    @staticmethod
    def skip_bom(file_path):
        """skip the BOM at the front of the file if present
           should really install chardet module and guess non BOM encoding too
           and check other sigs e.g. utf-16 see above get_bom_encoding()"""
        bom_length = min(32, os.path.getsize(file_path))

        with open(file_path, 'r+b') as fp:
            data = fp.read(bom_length)

        if data.startswith(codecs.BOM_UTF8):
            fp2 = open(file_path, encoding='utf-8-sig')
            return fp2
        # else:
        #     fp2 = open(file_path)
        #     return fp2
        else:
            fp2 = open(file_path, encoding='utf-8')
            return fp2

    def get_form(self, form_name):
        return self.form_repo.get_object(form_name)

    def get_data_set(self, data_name):
        return self.data_repo.get_object(data_name)

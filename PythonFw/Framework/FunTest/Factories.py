__author__ = 'david.hewitt'
from abc import ABCMeta, abstractmethod
from FunTest.Form import Form
import json
from FunTest.DataSet import DataSet
import csv
import os


class Factory(metaclass=ABCMeta):  # metaclass=ABCMeta allows @abstractmethod
    """base class for factories - caches the load"""
    def __init__(self, root_path, repo):
        self.cache = {}
        self.root_path = root_path
        self.repo = repo

    @abstractmethod
    def load(self, key):
        pass

    def get_object(self, key):
        if key not in self.cache:
            self.cache[key] = self.load(key)
        return self.cache[key]


class FormFactory(Factory):
    """factory for reading forms from the repo"""

    def form_path(self, form):
        return os.path.join(self.root_path, form + '.json')

    def load(self, key):
        load_path = self.form_path(key)
        with self.repo.get_file(load_path) as fp:  # note this will close when fp is out of scope(!)
            data = json.load(fp)
        return Form(key, data)


class DataFactory(Factory):
    """factory for reading forms from the repo"""

    def data_path(self, data):
        return os.path.join(self.root_path, data + '.csv')

    def load(self, key):
        load_path = self.data_path(key)
        with self.repo.get_file(load_path) as fp:  # note this will close when fp is out of scope(!)
            row_reader = csv.reader(fp, delimiter=',', quotechar='"')
            data_set = DataSet(key)
            for row in row_reader:
                if row:
                    data_set.append(row)
            return data_set

    @staticmethod
    def generate_template_from_form(repo, form_name, template_path, template_name):
        # form = repo.form_repo.get_object(form_name)
        # full_path = os.path.join(template_path, template_name + '.template.csv')
        # titles = ','.join(['"%s"' % title['Name'] for title in form.config["Inputs"]])
        # with open(full_path, 'w') as template:
        #     template.write(titles)
        #     template.write('\n')
        #     template.write(titles)
        # return full_path
        form = repo.form_repo.get_object(form_name)
        csv_path = os.path.join(template_path, template_name + '.csv')
        if os.path.exists(csv_path):
            #Get old title and data lines
            with open(csv_path,'r') as csv_reader:
                titles = csv_reader.readline().strip('\r\n')
                data_lines = csv_reader.readlines()
            #Updata new titles
            title_list = titles.replace(' ','').split(',')
            for title in form.config["Inputs"]:
                if title['Name'] not in title_list:
                    titles = titles + ',' + title['Name']
            #Write to file
            with open(csv_path, 'w') as template:
                template.writelines(titles)
                template.writelines('\n')
                template.writelines(data_lines)
        else:
            titles = ','.join(['"%s"' % title['Name'] for title in form.config["Inputs"]])
            titles = titles.replace('"','')
            with open(csv_path, 'w') as template:
                template.writelines(titles)
                template.writelines('\n')
                template.writelines(titles)
        return csv_path





__author__ = 'david.hewitt'
import json

from bs4 import BeautifulSoup

from FunTest.SoupSelect import select
import os


class Snap(object):
    @staticmethod
    def append_element(collection, html_element, html_element_type):
        # only map if they have an id or a name
        if 'id' in html_element.attrs:
            collection.append(Snap.build_description(html_element.attrs['id'], html_element_type, 'ID'))
        elif 'name' in html_element.attrs:
            collection.append(Snap.build_description(html_element.attrs['name'], html_element_type, 'Name'))
        #Add by phongtrinh to get the href elements
        elif 'href' in html_element.attrs:
            collection.append(Snap.build_description(html_element.text, html_element_type, 'PartialLinkText'))
        elif 'class' in html_element.attrs and html_element.attrs['class'] == 'field-validation-error':
            collection.append(Snap.build_description(html_element.attrs['class'], html_element_type, 'Class'))

    def process_feature(self, soup, selector, collection, html_element_type):
        for html_element in select(soup, selector):
            self.append_element(collection, html_element, html_element_type)

    def __init__(self, html):
        self.structure = {'Inputs': [], 'Triggers': [], 'Features': []}
        self.inputs = self.structure['Inputs']
        self.triggers = self.structure['Triggers']
        self.features = self.structure['Features']

        soup = BeautifulSoup(html)
        # todo: maybe map links, checkboxes etc
        self.process_feature(soup, 'input[type=text]',  self.inputs, 'TextBox')
        self.process_feature(soup, 'input[type=password]',  self.inputs, 'Password')
        self.process_feature(soup, 'select',  self.inputs, 'Select')
        self.process_feature(soup, 'textarea',  self.inputs, 'TextArea')
        self.process_feature(soup, 'input[type=submit]',  self.triggers, 'Button')
        self.process_feature(soup, 'input[type=button]',  self.triggers, 'Button')
        self.process_feature(soup, 'input[type=radio]', self.triggers, 'Button')
        self.process_feature(soup, 'button',  self.triggers, 'Button')
        self.process_feature(soup, 'span', self.features, 'PlainText')
        self.process_feature(soup, 'table', self.features, 'Table')
        self.process_feature(soup, 'input[type=checkbox]', self.inputs, 'CheckBox')
        self.process_feature(soup, 'a', self.triggers, 'Link')#Add by phongtrinh to get href elements
        # self.process_feature(soup, 'div', self.features, 'PlainText')

    @staticmethod
    def extract_name(html_id):
        parts = html_id.split('_')
        return parts[-1]

    @staticmethod
    def build_description(html_id, element_type, id_type):
        name = Snap.extract_name(html_id)
        desc = {'ID': html_id, 'IDByType': id_type, 'HtmlCtrlType': element_type, 'Name': name}
        return desc

    def serialize(self):
        json_string = json.dumps(self.structure, indent=4)
        return json_string

    def write(self, file_name):
        dir = os.path.dirname(file_name)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(file_name, 'w') as fp:
            s = self.serialize()
            fp.write(s)
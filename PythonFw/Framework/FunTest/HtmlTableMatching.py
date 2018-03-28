__author__ = 'david.hewitt'
import FunTest.Exceptions as Ex
from bs4 import BeautifulSoup
from FunTest.SoupSelect import select
from bs4.element import Tag
from FunTest.CodeGenerator import write_template, format_transform_list


class HtmlTableSchemaBuilder(object):

    def __init__(self, column_heading_selector, row_selector_list):
        self.column_heading_selector = column_heading_selector
        self.row_selector_list = row_selector_list

    # note we cn have multiple values in the column headers where multiple fields are mapped to a single column.
    @staticmethod
    def parse_column_item(header):
        if isinstance(header, str):
            return header
        elif isinstance(header, Tag):
            return header.text

        return ''

    # data can have blanks so skip_blank will be True
    @staticmethod
    def parse_column_list(col_list, skip_blank):
        return [y for y in
                [HtmlTableSchemaBuilder.parse_column_item(x).strip() for x in col_list]
                if len(y) > 0 or not skip_blank]

    @staticmethod
    def parse_columns(cols, skip_blank):
        return[HtmlTableSchemaBuilder.parse_column_list(z, skip_blank) for z in cols]

    def get_columns(self, browser):
        source = browser.page_source
        soup = BeautifulSoup(source)
        cols = select(soup, self.column_heading_selector)
        # flatten the column heading list - 1 transform per heading
        col_headings = [item for sub_list in self.parse_columns(cols, True) for item in sub_list]
        return col_headings

    def generate_table_mapper(self, browser, output_name, output_path):
        columns = self.get_columns(browser)
        column_string = format_transform_list(columns)

        replacement_dictionary = {
            'name': output_name,
            'transforms': column_string,
            'column_heading_selector': self.column_heading_selector,
            'row_selector': repr(self.row_selector_list)}

        write_template('DbTableSchema',  output_path, output_name, replacement_dictionary)


class BaseHtmlTableComparison(object):

    def __init__(self, column_heading_selector, row_selector_list, transform_dictionary):
        self.column_heading_selector = column_heading_selector
        self.row_selector_list = row_selector_list
        self.transform_dictionary = transform_dictionary

        # todo: this is a copy and paste from the TableSchema stuff - refactor
    def construct_value(self, row, key):
        value_source = self.transform_dictionary[key]
        if isinstance(value_source, str):
            return row.data[value_source.lower()]
        else:
            return value_source(row)

    # so no values in actual list NOT in expected list and
    # no values in expected list NOT in actual list
    # IGNORING BLANKS
    @staticmethod
    def compare_lists(supply_list, check_list):
        return [(i, i in check_list) for i in supply_list if len(i.strip()) > 0]

    # note that some columns contain more that one value
    # we only check to make sure that the expected value is in here some where
    def compare_html_row(self, to_process):
        for (column_names, expected_values), actual_values in to_process:
            values_exist_in_table = self.compare_lists(expected_values, actual_values)
            # do we care about extra values - they may not be being checked
            # unexpected value in table = compare_lists(actual_values, expected_values)
            # also note there can (because of mark up) be more values (typ blank) in html column
            # than expected
            if False in [present for (value, present) in values_exist_in_table]:
                return False
        return True

    def capture_rows(self, soup):
        html_table_rows = []
        for selector in self.row_selector_list:
            html_table_rows.extend(select(soup, selector))

        return html_table_rows

    def check_for_row_match(self, html_table_rows, transform_structure):
        for row in html_table_rows:
            # row data is a list of lists - the contained list may be empty
            row_data = HtmlTableSchemaBuilder.parse_columns(row, False)
            # iterator on (([col_names], [transformed_values]), [row_values])
            to_process = zip(transform_structure, row_data)
            if self.compare_html_row(to_process):
                return True

        return False

    def compare_data_with_html_table(self, browser, data):
        # in case column order changes - read actual column order and use as index
        source = browser.page_source
        soup = BeautifulSoup(source)
        cols = select(soup, self.column_heading_selector)
        html_table_rows = self.capture_rows(soup)

        # assume parameter transform_dictionary -> col name => transform(data)
        # assembles into expected structure for multiple data items per column
        transform_result = dict([(key, self.construct_value(data,key))for key in self.transform_dictionary])
        transform_structure = [[z for z in zip(i, [transform_result[x] for x in i])] for i in cols]

        if not self.check_for_row_match(html_table_rows, transform_structure):
            column_names = [col for (col, value) in transform_structure]
            column_values = [value for (col, value) in transform_structure]
            raise Ex.MissingTableValueException(column_names, column_values)

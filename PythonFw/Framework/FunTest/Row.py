__author__ = 'david.hewitt'
import FunTest.Exceptions as Ex


class Row(object):
    """data converted to dictionary"""
    options_list = ".options"
    errors_list = ".errors"
    table = ".table"

    def __init__(self, data_set, data):
        self.data_set = data_set
        self.data = []

        tmp_data = list(zip(data_set.columns, data))
        for item in tmp_data:
            tmp_item = list(item)
            if tmp_item[0] not in self.data_set.not_striped_columns:
                tmp_item[1] = tmp_item[1].strip()
            self.data.append(tmp_item)

        self.data = dict(self.data)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.get_string_index() + ',' + self.get_string_description()

    @staticmethod
    def form_key_string(*args):
        """format of the key used for pulling specific rows"""
        a = '^'.join(args)
        return a

    def get_index(self):
        return {k: self.data[k] for k in self.data_set.indexes}

    def get_string_index(self):
        list_values = [x for x in self.get_index().values()]
        # * to convert list to arg list
        return Row.form_key_string(*list_values)

    def get_string_description(self):
        list_values = [x for x in self.get_description().values()]
        # * to convert list to arg list
        return Row.form_key_string(*list_values)

    def get_description(self):
        return {k: self.data[k] for k in self.data_set.descriptions}

    def check_value_in_error_list(self, browser, ctl, value):
        error_list_key = ctl.data_id + Row.errors_list
        if error_list_key in self.data:
            error_list = self.data[error_list_key].split(';')
            ctl.error_list_match(error_list)

            if value is not None and value not in error_list:
                raise Ex.DataMismatchException(ctl.data_id, value, error_list)

    def check_a_table_row(self, ctl):
        table_key = ctl.data_id + Row.table
        if table_key in self.data:
            cell_list = self.data[table_key].split(';')
            ctl.table_row_match(cell_list)


    def check_value_in_option_list(self, browser,  ctl, value):
        option_list_key = ctl.data_id + Row.options_list
        if option_list_key in self.data:
            option_list = self.data[option_list_key].split(';')

            # this will raise an error if the control does not support an option list
            # will raise an error if the lists don't match (control and data.options
            ctl.option_list_match(option_list)

            # if value is not None and value not in option_list:
            #     raise Ex.OptionValueMismatchException(ctl.data_id, value, option_list)

    def compare(self, browser, ctl):
        partial_ctl_id = '^' + ctl.data_id
        if ctl.data_id in self.data:
            data_value = self.data[ctl.data_id]
        elif partial_ctl_id in self.data:
            data_value = self.data[partial_ctl_id]
        else:
            data_value = None

        # check options constraints
        self.check_value_in_option_list(browser, ctl, data_value)
        # check error list
        self.check_value_in_error_list(browser, ctl, data_value)
        # check a row of table matches with a row data in csv
        self.check_a_table_row(ctl)

        # check value for absolute match
        if ctl.data_id in self.data:
            if data_value != ctl.get_value() and data_value is not None:
                raise Ex.DataMismatchException(ctl.data_id, ctl.get_value(), self.data[ctl.data_id])
        # check value for partial match
        if partial_ctl_id in self.data:
            if ctl.get_value().find(data_value) == -1:
                raise Ex.DataHasNotContainStringException(ctl.data_id, ctl.get_value(), self.data[partial_ctl_id])

    def set(self, browser, ctl):
        if ctl.data_id in self.data:
            data_value = self.data[ctl.data_id]
        else:
            data_value = None

        # check options constraints
        self.check_value_in_option_list(browser, ctl, data_value)

        if data_value is not None:
            ctl.set_value(data_value)


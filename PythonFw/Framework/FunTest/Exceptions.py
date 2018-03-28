__author__ = 'david.hewitt'


class FunTestException(Exception):
    def __init__(self):
        pass


class WindowNotFoundException(FunTestException):
    def __init__(self, title):
        self.title = title

    def __str__(self):
        return "Window page %s  not found" % (self.title)


class ElementNotFoundException(FunTestException):
    def __init__(self, by_type, elem_id):
        self.by_type = by_type
        self.elem_id = elem_id

    def __str__(self):
        return "Element %s of type %s not found" % (self.elem_id, self.by_type)


class ControlToClickDoesNotExistInConfigException(FunTestException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "The control to click %s was not found in the config file" % self.name


class ElementDoesNotExistInConfigException(FunTestException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "The element %s was not found in the config file" % self.name


class UnexpectedElementException(FunTestException):
    def __init__(self, by_type, elem_id):
        self.by_type = by_type
        self.elem_id = elem_id

    def __str__(self):
        return "Unexpected element %s of type %s was found" % (self.elem_id, self.by_type)


class UnexpectedURLException(FunTestException):
    def __init__(self, expected_url, actual_url):
        self.expected_url = expected_url
        self.actual_url = actual_url

    def __str__(self):
        return "Unexpected url %s found. Expecting %s." % (self.actual_url, self.expected_url)


class RepoExistsException(FunTestException):
    def __init__(self, name, path_name):
        self.name = name
        self.path_name = path_name

    def __str__(self):
        return "Repository %s already exists at %s" % (self.name, self.path_name)


class DataMismatchException(FunTestException):
    """exception thrown when field value does not match the expected value"""
    def __init__(self, name, ctl_value, data_value):
        self.name = name
        self.ctl_value = ctl_value
        self.data_value = data_value

    def __str__(self):
        return 'Control %s value %s does not equal expected value %s' % (self.name, self.ctl_value,  self.data_value)


class DataHasNotContainStringException(FunTestException):
    """exception thrown when field value has not contain the expected value"""
    def __init__(self, name, ctl_value, data_value):
        self.name = name
        self.ctl_value = ctl_value
        self.data_value = data_value

    def __str__(self):
        return 'Control %s value %s has not contain expected value %s' % (self.name, self.ctl_value,  self.data_value)


class OptionValueMismatchException(FunTestException):
    """
        exception thrown when option value does not match the list of expected values
        also thrown if the list of expected options does not match the list available
    """
    def __init__(self, name, option_value, option_list):
        self.name = name
        self.option_value = option_value
        self.option_list = option_list

    def __str__(self):
        return 'Control %s value %s is not in list %s' % (self.name, repr(self.option_value),  repr(self.option_list))


class TableRowValueMismatchException(FunTestException):
    """
        exception thrown when option value does not match the list of expected values
        also thrown if the list of expected options does not match the list available
    """
    def __init__(self, name, table_value):
        self.name = name
        self.table_value = table_value

    def __str__(self):
        return 'Control %s value %s is not in table' % (self.name, repr(self.table_value))


class ControlDoesNotSupportOptionsException(FunTestException):
    """exception thrown when field value does not match the expected value"""
    def __init__(self, data_id):
        self.data_id = data_id

    def __str__(self):
        return 'Control %s does not support option lists.' % self.data_id


class KeyMissingException(FunTestException):
    """exception thrown when field value does not match the expected value"""
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return repr(self.key)


class TooManyRowsError(FunTestException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TooFewRowsError(FunTestException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DbCheckFailedException(FunTestException):

    def __init__(self, fail_list):
        self.fail_list = fail_list

    def __str__(self):
        return repr(self.fail_list)


class MissingTableValueException(FunTestException):

    def __init__(self, column_names, expected_values):
        self.column_names = column_names
        self.expected_values = expected_values

    def __str__(self):
        pattern = "The column(s) %s Were expected to contain %s."
        columns = repr(self.column_names)
        expected_values = repr(self.expected_values)
        return pattern % (columns, expected_values)


class FileNotFound(FunTestException):

    def __init__(self, infile):
        self.infile = infile

    def __str__(self):
        pattern = "File %s not found."
        infile = repr(self.infile)
        return pattern %(infile)
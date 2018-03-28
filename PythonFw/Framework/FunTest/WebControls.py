__author__ = 'david.hewitt'
from selenium.webdriver.support.ui import Select
import FunTest.Exceptions as Ex
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
LOGGER.setLevel(logging.ERROR)

class WebControlBase(object):

    def __init__(self, browser, element_id, selenium_control, data_id, by):
        self.browser = browser
        self.element_id = element_id
        self.selenium_control = selenium_control
        # data ids are lowered for case insensitive comparison
        # with data column tiles (also lowered)
        self.data_id = data_id.lower()
        self.by = by

    def click(self):
        self.browser.execute_script("arguments[0].focus()", self.selenium_control)
        self.selenium_control.click()

    def click_by_js(self):
        self.browser.execute_script("arguments[0].click()", self.selenium_control)

    def is_enabled(self):
        return self.selenium_control.is_enabled()

    def is_disabled(self):
        return ~self.selenium_control.is_enabled()

    def option_list_match(self, option_list):
        raise Ex.ControlDoesNotSupportOptionsException(self.data_id)

    def move_to_element(self):
        actions = ActionChains(self.browser)
        actions.move_to_element(self.selenium_control).perform()

    def wait_for_page_load(self, timeout = 20):
        js_script = "try {"+\
        "  if (document.readyState !== 'complete') {"+\
        "    return false;"\
        "  }"+\
        "  if (window.jQuery) {" +\
        "    if (window.jQuery.active) {"\
        "      return false;"+\
        "    } else if (window.jQuery.ajax && window.jQuery.ajax.active) {"+\
        "      return false;"+\
        "    }"+\
        "  }"+\
        "  if (window.angular) {"+\
        "    if (!window.qa) {"+\
        "      window.qa = {"+\
        "        doneRendering: false"+\
        "      };"+\
        "    }"+\
        "    var injector = window.angular.element('body').injector();"+\
        "    var $rootScope = injector.get('$rootScope');"+\
        "    var $http = injector.get('$http');"+\
        "    var $timeout = injector.get('$timeout');"+\
        "    if ($rootScope.$$phase === '$apply' || $rootScope.$$phase === '$digest' || $http.pendingRequests.length !== 0) {"+\
        "      window.qa.doneRendering = false;"+\
        "      return false;"+\
        "    }"+\
        "    if (!window.qa.doneRendering) {"+\
        "      $timeout(function() {"+\
        "        window.qa.doneRendering = true;"+\
        "      }, 0);"+\
        "      return false;"+\
        "    }"+\
        "  }"+\
        "  return true;"+\
        "} catch (ex) {"+\
        "  return false;"+\
        "}"
        try:
            for i in range(timeout):
                if self.browser.execute_script(js_script) == True:
                    break
                else:
                    time.sleep(1)
        except:
            pass

class CombineBoxControl(WebControlBase):
    """interaction with a Combo box combined with Text Box"""
    def set_value(self, value):
        for i in range(5):
            try:
                self.selenium_control.click()
                self.selenium_control.send_keys(Keys.CONTROL, "a")
                self.selenium_control.send_keys(value)
                self.selenium_control.send_keys(Keys.TAB)
                self.selenium_control.send_keys(Keys.TAB)
                break
            except (StaleElementReferenceException, NoSuchElementException):
                time.sleep(2)
                self.selenium_control = self.browser.find_element(self.by, self.element_id)

    def get_value(self):
        pass

class TableControl(WebControlBase):
    """interaction with a table control"""
    def set_value(self,value):
        pass

    def get_value(self):
        pass

    def table_row_match(self, cell_list_expected_data):
        row_web_elements_list = self.selenium_control.find_elements_by_tag_name('tr')
        row_actual_data_list = []
        for row_web_element in row_web_elements_list:
            cell_web_elements_list = row_web_element.find_elements_by_tag_name('td')
            row_actual_data = []
            for cell in cell_web_elements_list:
                row_actual_data.append(cell.text)
            row_actual_data_list.append(row_actual_data)
        if cell_list_expected_data not in row_actual_data_list:
            raise Ex.TableRowValueMismatchException(self.data_id,cell_list_expected_data)

class FrameControl(WebControlBase):
    """interaction with a iframe"""
    def switch_to_iframe(self):
        self.browser.switch_to.frame(self.selenium_control)

class TextBoxControl(WebControlBase):
    """interaction with a textbox like control"""
    def set_value(self, value):
        for i in range(5):
            try:
                self.selenium_control.click()
                self.selenium_control.clear()
                text = self.selenium_control.get_attribute("value").strip()
                if text != "":
                    self.selenium_control.send_keys(Keys.END)
                    for i in range(len(text)):
                        self.selenium_control.send_keys(Keys.BACKSPACE)

                self.selenium_control.send_keys(value)
                self.selenium_control.send_keys(Keys.TAB)
                #self.browser.execute_script("arguments[0].blur();", self.selenium_control)
                break
            except (StaleElementReferenceException, NoSuchElementException):
                time.sleep(2)
                self.selenium_control = self.browser.find_element(self.by, self.element_id)

    def get_value(self):
        return self.selenium_control.get_attribute('value')


class SelectControl(WebControlBase):
    """interaction with a textbox like control"""
    def set_value(self, value):
        if value:
            for i in range(5):
                try:
                    page_source_before = self.browser.page_source
                    select = Select(self.selenium_control)
                    select.select_by_value(value)
                    for j in range(10):
                        page_source_after = self.browser.page_source
                        if(page_source_after != page_source_before):
                            break
                        else:
                            j += 1
                            time.sleep(1)
                    break
                except StaleElementReferenceException:
                    time.sleep(2)
                    self.selenium_control = self.browser.find_element(self.by, self.element_id)
        else:
            pass

    def get_value(self):
        select = Select(self.selenium_control)
        return select.first_selected_option.get_attribute("value")

    def get_text(self):
        select = Select(self.selenium_control)
        return select.first_selected_option.text

    def option_list_match(self, option_list):
        select = Select(self.selenium_control)
        actual_options = [option.text for option in select.options]
        # actual_options = [option.get_attribute('value') for option in select.options]
        if len(option_list) != len(actual_options):
            raise Ex.OptionValueMismatchException(self.data_id, option_list, actual_options)

        for option in option_list:
            if option not in actual_options:
                raise Ex.OptionValueMismatchException(self.data_id, option, actual_options)


class CheckBox(WebControlBase):
    """interaction with a textbox like control"""
    def set_value(self, value):
        current = self.selenium_control.is_selected()
        if value == 'True' and not current:
            self.selenium_control.click()
        elif value == 'False' and current:
            self.selenium_control.click()

    def get_value(self):
        value = self.selenium_control.is_selected()
        if value:
            return 'True'
        else:
            return 'False'


class SetValueOnStaticHtml(Exception):
    def __init__(self, element_id, value):
        self.element_id = element_id
        self.value = value


class StaticControl(WebControlBase):
    """interaction with a textbox like control"""
    def set_value(self, value):
        raise SetValueOnStaticHtml(self.element_id, value)

    def get_value(self):
        if self.selenium_control.text != "":
            text = self.selenium_control.text
        elif self.selenium_control.get_attribute("value") != None:
            text = self.selenium_control.get_attribute("value")
        else:
            text = ''
        return text

    def error_list_match(self, error_list):
        for error_text in error_list:
            if self.selenium_control.text.find(error_text) == -1:
                raise Ex.DataMismatchException(self.data_id, error_list, self.selenium_control.text)


class ButtonControl(WebControlBase):
    """interaction with a textbox like control"""
    def set_value(self, value):
        raise SetValueOnStaticHtml(self.element_id, value)

    def get_value(self):
        return self.selenium_control.Text


__author__ = 'david.hewitt'

import FunTest.Exceptions as Ex

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from FunTest.WebControls import TextBoxControl, SelectControl, CheckBox, StaticControl, ButtonControl, TableControl, CombineBoxControl, FrameControl
import time


class Form(object):
    """representation of the structure of a web form"""
    control_map = {
        'TextBox': TextBoxControl,
        0: TextBoxControl,
        'Select': SelectControl,
        1: SelectControl,
        'Password': TextBoxControl,
        2: TextBoxControl,
        'TextArea': TextBoxControl,
        3: TextBoxControl,
        'CheckBox': CheckBox,
        4: CheckBox,
        'Button': ButtonControl,
        5: ButtonControl,
        'Link': StaticControl,
        6: StaticControl,
        'Label': StaticControl,
        7: StaticControl,
        'PlainText': StaticControl,
        8: StaticControl,
        'Table': TableControl,
        9: TableControl,
        'ComboBox': CombineBoxControl,
        10: CombineBoxControl,
        'Iframe': FrameControl,
        11: FrameControl,
        }

    by_map = {
        'ID': By.ID,
        0: By.ID,
        'PartialLinkText': By.PARTIAL_LINK_TEXT,
        1: By.PARTIAL_LINK_TEXT,
        'Name': By.NAME,
        2: By.NAME,
        'Class': By.CLASS_NAME,
        3: By.CLASS_NAME,
        'Xpath': By.XPATH,
        4: By.XPATH
        }

    def __init__(self, name, config, timeout=30):
        self.name = name
        self.config = config
        self.timeout = timeout

    def get_control(self, browser, json_dict, expected_missing=False, **kwargs):
        """fetch a WebControl"""
        id_type = json_dict['IDByType']
        element_id = json_dict['ID']
        element_type = json_dict['HtmlCtrlType']
        data_id = json_dict['Name']
        by = Form.by_map[id_type]
        if 'timeout' in kwargs:
            time_out = kwargs['timeout']
        else:
            time_out = self.timeout

        try:
            self.wait_for_page_load(browser)
            element = WebDriverWait(browser, time_out).until(EC.visibility_of_element_located((by, element_id)))
            if not expected_missing:
                return Form.control_map[element_type](browser, element_id, element, data_id, by)
            else:
                raise Ex.UnexpectedElementException( by, element_id)

        except TimeoutException:
            if not expected_missing:
                raise Ex.ElementNotFoundException( by, element_id)
            else:
                return None

    def wait_for_page_load(self, browser, timeout = 20):
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
                if browser.execute_script(js_script) == True:
                    break
                else:
                    time.sleep(1)
        except:
            pass

    def check(self, browser, data, expected_missing=False, control_name=None, **kwargs):
        if "Features" in self.config:
            # note this will check the inner html typically
            for item in self.config["Features"]:
                if control_name != None and item["Name"] == control_name:
                    ctl = self.get_control(browser, item, expected_missing, **kwargs)
                    return
                else:
                    ctl = self.get_control(browser, item, expected_missing, **kwargs)
                    if data is not None and ctl is not None:
                        data.compare(browser, ctl)

        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                ctl = self.get_control(browser, item, expected_missing, **kwargs)

        if "Triggers" in self.config:
            for item in self.config["Triggers"]:
                ctl = self.get_control(browser, item, expected_missing, **kwargs)

    def set(self, browser, data, **kwargs):
        for item in self.config["Inputs"]:
            ctl = self.get_control(browser, item, **kwargs)
            data.set(browser, ctl)
            self.wait_for_page_load(browser)

    def click(self, browser, control_name, **kwargs):
        if "Triggers" in self.config:
            for item in self.config["Triggers"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.click()
                    return
        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.click()
                    return
        if "Features" in self.config:
            for item in self.config["Features"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.click()
                    return

        raise Ex.ControlToClickDoesNotExistInConfigException( control_name)

    def click_by_js(self, browser, control_name, **kwargs):
        if "Triggers" in self.config:
            for item in self.config["Triggers"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.click_by_js()
                    return
        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.click_by_js()
                    return
        if "Features" in self.config:
            for item in self.config["Features"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.click_by_js()
                    return

        raise Ex.ControlToClickDoesNotExistInConfigException( control_name)

    def switch_to_iframe(self, browser, control_name, **kwargs):
        if "Triggers" in self.config:
            for item in self.config["Triggers"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.switch_to_iframe()
                    return
        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.switch_to_iframe()
                    return
        if "Features" in self.config:
            for item in self.config["Features"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.switch_to_iframe()
                    return

        raise Ex.ElementDoesNotExistInConfigException(control_name)

    def element_is_present(self, browser, control_name, timeout=None, **kwargs):
        element = None
        if "Triggers" in self.config:
            for trigger in self.config["Triggers"]:
                if trigger["Name"] == control_name:
                    element = trigger
                    break
        if "Inputs" in self.config:
            for input in self.config["Inputs"]:
                if input["Name"] == control_name:
                    element = input
                    break
        if "Features" in self.config:
            for feature in self.config["Features"]:
                if feature["Name"] == control_name:
                    element = feature
        if element is None:
            raise Ex.ElementDoesNotExistInConfigException(control_name)

        id_type = element['IDByType']
        element_id = element['ID']
        by = Form.by_map[id_type]

        try:
            if timeout is None:
                timeout = 30
            else:
                timeout = timeout
            WebDriverWait(browser, timeout=timeout).until(EC.visibility_of_element_located((by, element_id)))
            return True
        except TimeoutException:
            return False

    def element_is_enabled(self, browser, control_name, **kwargs):
        element = None
        if "Triggers" in self.config:
            for trigger in self.config["Triggers"]:
                if trigger["Name"] == control_name:
                    element = trigger
                    break
        if "Inputs" in self.config:
            for input in self.config["Inputs"]:
                if input["Name"] == control_name:
                    element = input
                    break
        if "Features" in self.config:
            for feature in self.config["Features"]:
                if feature["Name"] == control_name:
                    element = feature
                    break
        if element is None:
            raise Ex.ElementDoesNotExistInConfigException(control_name)

        web_element = self.get_control(browser, element)

        return web_element.is_enabled()

    def element_is_disabled(self, browser, control_name, **kwargs):
        element = None
        if "Triggers" in self.config:
            for trigger in self.config["Triggers"]:
                if trigger["Name"] == control_name:
                    element = trigger
                    break
        if "Inputs" in self.config:
            for input in self.config["Inputs"]:
                if input["Name"] == control_name:
                    element = input
                    break
        if "Features" in self.config:
            for feature in self.config["Features"]:
                if feature["Name"] == control_name:
                    element = feature
        if element is None:
            raise Ex.ElementDoesNotExistInConfigException(control_name)

        web_element = self.get_control(browser, element)

        return web_element.is_disabled()

    def element_is_invisible(self, browser, control_name, timeout=None):
        element = None
        if "Triggers" in self.config:
            for trigger in self.config["Triggers"]:
                if trigger["Name"] == control_name:
                    element = trigger
                    break
        if "Inputs" in self.config:
            for input in self.config["Inputs"]:
                if input["Name"] == control_name:
                    element = input
                    break
        if "Features" in self.config:
            for feature in self.config["Features"]:
                if feature["Name"] == control_name:
                    element = feature
        if element is None:
            raise Ex.ElementDoesNotExistInConfigException(control_name)

        id_type = element['IDByType']
        element_id = element['ID']
        by = Form.by_map[id_type]

        try:
            if timeout is None:
                timeout = 30
            else:
                timeout = timeout
            WebDriverWait(browser, timeout=timeout).until(EC.invisibility_of_element_located((by, element_id)))
            return True
        except TimeoutException:
            return False

    def text_element_changed(self, browser, control_name, text):
        element = None
        if "Triggers" in self.config:
            for trigger in self.config["Triggers"]:
                if trigger["Name"] == control_name:
                    element = trigger
                    break
        if "Inputs" in self.config:
            for input in self.config["Inputs"]:
                if input["Name"] == control_name:
                    element = input
                    break
        if "Features" in self.config:
            for feature in self.config["Features"]:
                if feature["Name"] == control_name:
                    element = feature
        if element is None:
            raise Ex.ElementDoesNotExistInConfigException(control_name)

        id_type = element['IDByType']
        element_id = element['ID']
        by = Form.by_map[id_type]

        try:
            WebDriverWait(browser, timeout=30).until(EC.text_to_be_present_in_element_value((by, element_id), text))
            return True
        except TimeoutException:
            return False

    def move_to_element(self, browser, control_name, **kwargs):
        if "Triggers" in self.config:
            for item in self.config["Triggers"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.move_to_element()
                    return

        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.move_to_element()
                    return

        if "Features" in self.config:
            for item in self.config["Features"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.move_to_element()
                    return

        raise Ex.ControlToClickDoesNotExistInConfigException(control_name)

    """This method is added by phong trinh to input a text to an input"""
    def set_an_input(self, browser, control_name, string, **kwargs):
        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    ctl.set_value(string)
                    return

    def get_text_element(self, browser, control_name, **kwargs):

        if "Features" in self.config:
            for item in self.config["Features"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    return ctl.get_value()

        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    return ctl.get_value()

        if "Triggers" in self.config:
            for item in self.config["Triggers"]:
                if item["Name"] == control_name:
                    ctl = self.get_control(browser, item, **kwargs)
                    return ctl.get_value()
        raise Ex.ControlToClickDoesNotExistInConfigException(control_name)


    def get_text_ddl(self, browser, control_name, **kwargs):

        if "Inputs" in self.config:
            for item in self.config["Inputs"]:
                if item["Name"] == control_name and (item["HtmlCtrlType"] == 'Select' or item["HtmlCtrlType"] == 1):
                    ctl = self.get_control(browser, item, **kwargs)
                    return ctl.get_text()
        raise Ex.ControlToClickDoesNotExistInConfigException(control_name)
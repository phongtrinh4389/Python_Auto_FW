__author__ = 'david.hewitt'
import os
import inspect
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
import FunTest.Exceptions as Ex
from FunTest.WebSnapShot import Snap
from FunTest.Repository import Repo
from FunTest.Exceptions import *
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import *


class BrowserType(object):
    """Supported browsers"""
    Ie = 'Ie'
    Chrome = 'Chrome'
    Firefox = 'Firefox'

class Constant(object):
    """Defining constants"""
    IMPLICIT_WAIT = 20
    DEFAULT_TIMEOUT = 30
    SMALL_TIMEOUT = 20


def get_path():
    """Needs to be in file that it is being used to find the directory of"""
    this_path = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
    return os.path.realpath(os.path.abspath(this_path))


def get_tests_dir():
    """"""
    root_path = os.path.dirname(os.path.dirname(get_path()))
    test_path = root_path + '\\Automated Tests\\'
    return test_path


def create_browser(default_browser, browser, **kwargs):
    """
       Takes the kwargs no_ui=True to stop loading a browser and
       driver=BrowserType.x to select a browser - otherwise
       uses default_browser == BrowserType.x
    """
    if browser is not None:
        return browser

    if 'no_ui' in kwargs and kwargs['no_ui']:
        return None

    if (default_browser == BrowserType.Ie and 'driver' not in kwargs) or \
            ('driver' in kwargs and kwargs['driver'] == BrowserType.Ie):
        ie_driver = get_path()+'\driver\IEDriverServer'
        capabilities = {'ignoreZoomSetting': True, "requireWindowFocus": False, "nativeEvents": False}
        driver = webdriver.Ie(ie_driver, capabilities=capabilities)
        driver.implicitly_wait(Constant.IMPLICIT_WAIT)
        return driver

    elif (default_browser == BrowserType.Chrome and 'driver' not in kwargs) or \
            ('driver' in kwargs and kwargs['driver'] == BrowserType.Chrome):
        chrome_driver = get_path()+'\driver\chromedriver'
        driver = webdriver.Chrome(chrome_driver)
        driver.implicitly_wait(Constant.IMPLICIT_WAIT)
        return driver

    elif (default_browser == BrowserType.Firefox and 'driver' not in kwargs) or \
            ('driver' in kwargs and kwargs['driver'] == BrowserType.Firefox):
        # this is to stop the 'what do you want to send to firefox' bar popping up
        # by loading a profile that has the answer
        root_path = os.path.dirname(os.path.dirname(get_path()))
        profile_path = os.path.join(root_path, 'CashfacFramework', 'FireFox')
        fp = FirefoxProfile(profile_path)
        gecko_driver = get_path() + '\driver\geckodriver'
        driver = webdriver.Firefox(firefox_profile=fp, executable_path=gecko_driver)
        # driver.delete_all_cookies()
        driver.implicitly_wait(Constant.IMPLICIT_WAIT)
        return driver


class TestFramework(object):
    """Selenium Web driver based web test support.
    Allows the use of template and data files in test cases
    provides a facade over the above classes
    acts a a facade over the various components"""

    def __init__(self, base_url, test_repo, browser, default_browser, db_tester, step_delay=0, version=None, **kwargs):
        """Constructor that captures the basic configuration of the system under test"""
        self.baseUrl = base_url
        self.repo = Repo(test_repo)
        self.version = version
        self.default_browser = default_browser
        self.browser = create_browser(default_browser, browser, **kwargs)
        self.db_tester = db_tester
        # This is applied only for Azure
        # self.snapshot_dir = os.path.join(self.repo.root, 'Snapshot')
        self.snapshot_dir = os.path.join('F:\\Data\\', 'Snapshot')
        self.step_delay = step_delay

    def load_data(self, data_name):
        """Loads a data file - data_name is key for file typically
           the file name without any extension"""
        return self.repo.get_data_set(data_name)

    def request(self, url):
        """Use Selenium Web Driver to navigate the browser to a specific URL"""
        if url.startswith('/'):
            url = url[1:]  # this will return '' for a url of '/'
        full_url = self.baseUrl + url
        if self.browser is not None:
            self.browser.get(full_url)
            self.browser.maximize_window()

    def request_full_url(self, url):
        """Use Selenium Web Driver to navigate the browser to a full URL"""
        if url.startswith('/'):
            url = url[1:]  # this will return '' for a url of '/'
        if self.browser is not None:
            self.browser.get(url)
            self.browser.maximize_window()

    def test_url(self, expected_url):
        """Check that the current URL is the expected URL
           Note that this does not wait to see if there is
           a request running - check the HTML first"""
        if expected_url.startswith('/'):
            expected_url = expected_url[1:]  # this will return '' for a url of '/'
        full_url = (self.baseUrl + expected_url).lower()
        actual_url = self.browser.current_url.lower()
        if actual_url != full_url:
            raise Ex.UnexpectedURLException(full_url, actual_url)

    def check_html(self, form_name, **kwargs):
        """Check the HTML against a form configuration file
           The test will wait to see if the elements appear
           in case there is an Ajax requires running etc"""
        time.sleep(self.step_delay)
        self.check_html_and_data(form_name, None, **kwargs)

    def check_html_for_unexpected_elements(self, form_name, control_name = None, **kwargs):
        """Check the HTML against a form configuration file
           that contains elements that should NOT appear
           again the code will wait to see if the elements appear"""
        self.check_html_and_data(form_name, None, True, control_name, **kwargs)

    def check_html_and_data(self, form_name, data, expected_missing=False, control_name=None, **kwargs):
        """This will both check that the HTML in the browser
           matches a form configuration AND that the values in the
           input elements match the supplied Row"""
        time.sleep(self.step_delay)
        form = self.repo.form_repo.get_object(form_name)
        if data is None:
            form.check(self.browser, data, expected_missing, control_name, **kwargs)
            return
        else:
            exception = None
            for i in range(30):
                try:
                    form.check(self.browser, data, expected_missing, control_name, **kwargs)
                    return
                except ElementNotFoundException as e:
                    raise e
                except Exception as e:
                    exception = e
                    time.sleep(1)
            raise exception

    def fill_form(self, form_name, data, **kwargs):
        """This will use the supplied data Row and use
           the supplied Form to fill the input elements
           on the current page"""
        form = self.repo.form_repo.get_object(form_name)
        form.set(self.browser, data, **kwargs)
        time.sleep(self.step_delay)

    def upload_file(self, file_path, **kwargs):
        """Upload a file"""
        elem = self.browser.find_element(By.XPATH, "//*[@type='file']")
        self.browser.execute_script("arguments[0].style.display = 'block';", elem)
        elem.send_keys(file_path)

    def click(self, form_name, control_name, **kwargs):
        """This method will click an element selected from
           the provided Form file given the friendly control name"""
        form = self.repo.form_repo.get_object(form_name)
        form.click(self.browser, control_name, **kwargs)

    def click_by_js(self, form_name, control_name, **kwargs):
        """This method will click an element selected from
           the provided Form file given the friendly control name"""
        form = self.repo.form_repo.get_object(form_name)
        form.click_by_js(self.browser, control_name, **kwargs)

    def switch_to_iframe(self, form_name, control_name, **kwargs):
        """This method will switch to an irame represent by control_name"""
        form = self.repo.form_repo.get_object(form_name)
        form.switch_to_iframe(self.browser, control_name, **kwargs)

    def switch_to_default_content(self, **kwargs):
        """This method will switch to the default page"""
        self.browser.switch_to.default_content()

    def find_element_by_link_text(self, link):
        WebDriverWait(self.browser, Constant.DEFAULT_TIMEOUT).until(EC.element_to_be_clickable((By.LINK_TEXT, link)))
        return self.browser.find_element_by_link_text(link)

    def wait_for_an_element_present(self, form_name, control_name, timeout=None, **kwargs):
        """This method will wait for an element present from
            the provided Form file given the friendly control name"""
        form = self.repo.form_repo.get_object(form_name)
        if form.element_is_present(self.browser, control_name, timeout=timeout):
            pass
        else:
            raise TimeoutException('Element %s is not visible' %control_name)

    def wait_for_text_element_changed(self, form_name, control_name, text, **kwargs):
        """This method will wait for an element present from
            the provided Form file given the friendly control name"""
        form = self.repo.form_repo.get_object(form_name)
        if form.text_element_changed(self.browser, control_name, text):
            pass
        else:
            raise TimeoutException('The text of Element %s is not changed' %control_name)

    def wait_for_an_element_invisible(self, form_name, control_name, timeout=None, **kwargs):
        """This method will wait for an element invisible"""
        form = self.repo.form_repo.get_object(form_name)
        if form.element_is_invisible(self.browser, control_name, timeout=timeout):
            pass
        else:
            raise TimeoutException('Element %s is still visible' %control_name)

    def wait_for_element_text_not_empty(self, form_name, control_name, **kwargs):
        """This method will wait for the text of an element changes"""
        for i in range(30):
            element_text = self.get_text_element( form_name, control_name)
            if element_text is not "":
                break

    def wait_for_page_loaded(self):
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
            for i in range(30):
                if self.browser.execute_script(js_script) == True:
                    break
                else:
                    time.sleep(1)
        except:
            pass

    def element_is_present(self, form_name, control_name, **kwargs):
        """This method is used to check whether an element present"""
        form = self.repo.form_repo.get_object(form_name)
        return form.element_is_present(self.browser, control_name)

    def element_is_invisible(self, form_name, control_name, **kwargs):
        """This method is used to check whether an element not present"""
        form = self.repo.form_repo.get_object(form_name)
        return form.element_is_invisible(self.browser, control_name)

    def element_is_enabled(self, form_name, control_name, **kwargs):
        """This method is used to check whether an element is enabled"""
        form = self.repo.form_repo.get_object(form_name)
        return form.element_is_enabled(self.browser, control_name)

    def element_is_disabled(self, form_name, control_name, **kwargs):
        """This method is used to check whether an element is disabled"""
        form = self.repo.form_repo.get_object(form_name)
        return form.element_is_disabled(self.browser, control_name)

    def move_to_element(self, form_name, control_name, **kwargs):
        """This method will move the cursor to an element"""
        form = self.repo.form_repo.get_object(form_name)
        form.move_to_element(self.browser, control_name, **kwargs)

    def capture_form(self, file_path):
        """This will parse the current HTML and write a Form
           file using the id's of the elements to provide
           best guesses for friendly names. It will need editing
           for use"""
        source = self.browser.page_source
        snap = Snap(source)
        snap.write(file_path)

    def capture_form_and_data(self,form_path,form_name, csv_path, csv_name):
        """Snapshot a page after it had changed and update a specific CSV file -
        it would add any missing columns, but NOT delete any missing ones since CSV files
        typically support more that one form."""
        source = self.browser.page_source
        snap = Snap(source)
        snap.write(form_path)
        self.create_data_template(form_name,csv_path,csv_name)

    def create_data_template(self, form_name, template_path, template_name):
        """Takes a Form name and creates a starter for a data file
           based on the contents of the Form file"""
        csv_path = self.repo.data_repo.generate_template_from_form(self.repo, form_name, template_path, template_name)
        return csv_path

    def create_comparison_template(self, table, template_path, name):
        """Creates a initial comparison template for the named table
           requires editing to be of use"""
        self.db_tester.create_comparison_template(table, template_path, name)

    def remove_snapshot(self):
        """removes the default snapshot from the configured database"""
        self.db_tester.clear_connections()
        self.db_tester.remove_snapshot()

    def create_snapshot(self):
        """Creates a snapshot of the configured database
           using the default name. It places the snapshot
           file in the repository. Note that this will prevent the repo
           from deletion until the snapshot is removed"""
        self.db_tester.clear_connections()
        self.db_tester.create_snapshot(self.snapshot_dir)

    def refresh_db_snapshot(self):
        """deletes the existing default snapshot and creates a fresh one
          Note that it runs the restore just to make sue the DB is in
          the correct initial state"""
        self.db_tester.clear_connections()
        self.db_tester.refresh_snapshots(self.snapshot_dir)

    def clear_connections(self):
        """Clear connections"""
        self.db_tester.clear_connections()

    def reset_iis(self):
        """Restart IIS to drop any database cached connections"""
        self.db_tester.reset_iis()

    def restore_db_from_snapshot(self):
        """restore the database from the default snapshot"""
        self.db_tester.clear_connections()
        self.db_tester.restore()

    def set_text_element(self, form_name, control_name, data, **kwargs):
        form = self.repo.form_repo.get_object(form_name)
        form.set_an_input(self.browser, control_name, data)

    def get_text_element(self, form_name, control_name, **kwargs):
        """Added by phong trinh to get text of element"""
        form = self.repo.form_repo.get_object(form_name)
        return form.get_text_element(self.browser,control_name)

    def get_text_ddl(self, form_name, control_name, **kwargs):
        """Added by phong trinh to get text of a dropdown list"""
        form = self.repo.form_repo.get_object(form_name)
        return form.get_text_ddl(self.browser,control_name)

    def input_random_password(self,form_name, user, message_pass_control,  partial_pass_1_control, partial_pass_2_control, partial_pass_3_control ):
        """Added by phongtrinh to input 3 random letters"""
        password = user.data['password']
        form = self.repo.form_repo.get_object(form_name)
        message = form.get_text_element(self.browser,message_pass_control)
        arrs = message.split()
        #Input random password characters
        form.set_an_input(self.browser,partial_pass_1_control,password[int(arrs[3].split(',')[0]) -1])
        form.set_an_input(self.browser,partial_pass_2_control,password[int(arrs[4].split(',')[0]) -1])
        form.set_an_input(self.browser,partial_pass_3_control,password[int(arrs[5].split(',')[0]) -1])

    def input_memorable_answer(self,form_name,answer,memorable_control):
        """Added by phongtrinh to input secret answer"""
        form = self.repo.form_repo.get_object(form_name)
        form.set_an_input(self.browser,memorable_control,answer)

    def capture_screen(self, path):
        try:
            self.browser.save_screenshot(path + '/test.jpeg')
        except Exception:
            pass

    @staticmethod
    def build_repo(name, url, default_db, db_list, db_server, root_dir):
        """Creates a new repository"""
        Repo.build_repo(name, url, default_db, db_list,db_server, root_dir)

    def quit(self):
        """Closes the browser"""
        self.capture_screen(get_tests_dir())
        self.browser.quit()

@contextmanager
def get_ctx(base_url, test_repo):
    """wrap a web browser in a context manager"""
    browser = webdriver.Firefox()
    try:
        tester = TestFramework(base_url, test_repo, browser)
        yield tester
    finally:
        browser.quit()
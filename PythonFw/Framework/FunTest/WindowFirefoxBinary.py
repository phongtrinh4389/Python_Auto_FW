__author__ = 'phongtrinh'
from selenium.webdriver.firefox.webdriver import FirefoxBinary
import platform
import os
from subprocess import Popen, STDOUT


class WindowsFirefoxBinary(FirefoxBinary):

    def _start_from_profile_path(self, path):
        self._firefox_env["XRE_PROFILE_PATH"] = path

        if platform.system().lower() == 'linux':
            self._modify_link_library_path()
        command = [self._start_cmd, "-silent"]
        if self.command_line is not None:
            for cli in self.command_line:
                command.append(cli)

        # Added stdin argument:
        nul = open(os.devnull, 'w+')
        Popen(command, stdin=nul, stdout=self._log_file or nul, stderr=STDOUT,
              env=self._firefox_env).communicate()
        command[1] = '-foreground'
        self.process = Popen(
            command, stdin=nul, stdout=self._log_file or nul, stderr=STDOUT,
            env=self._firefox_env)
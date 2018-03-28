__author__ = 'phongtrinh'

import logging
import os
import inspect

class Logger():

    @staticmethod
    def get_path():
        this_path = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        return os.path.realpath(os.path.abspath(this_path))

    @staticmethod
    def get_project_root():
        current = Logger.get_path()
        root = os.path.dirname(os.path.dirname(current))
        return root

    @staticmethod
    def get_file_path(*args):
        """Take location of the projecy root and add subdirectories + filename"""
        root = Logger.get_project_root()
        return os.path.join(root, *args)

    @staticmethod
    def set_console_logger(logger,level):
        logger.setLevel(level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        chFormatter = logging.Formatter('%(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s')
        console_handler.setFormatter(chFormatter)
        logger.addHandler(console_handler)
        return logger

    @staticmethod
    def get_logger():
        logger_path = Logger.get_file_path('PyTutorial','Logger','log_file.log')
        logging.basicConfig(
                        format='%(asctime)s %(filename)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=logger_path,
                        level=logging.DEBUG)
        logger = logging.getLogger()
        # Logger.set_console_logger(logger,level)
        return logger
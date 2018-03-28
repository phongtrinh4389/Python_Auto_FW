__author__ = 'david.hewitt'

import os
import sys
import inspect
from subprocess import call

# Info:
# cmd_folder = os.path.dirname(os.path.abspath(__file__)) # DO NOT USE __file__ !!!
# __file__ fails if script is called in different ways on Windows
# __file__ fails if someone does os.chdir() before
# sys.argv[0] also fails because it doesn't not always contains the path
#  realpath() will make your script run, even if you symlink it :)
# to add current path


# use this if you want to include modules from a subfolder
def add_current_path():
    cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)


def add_sub_folder(folder):
    this_path = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
    cmd_sub_folder = os.path.realpath(os.path.abspath(os.path.join(this_path, folder)))
    if cmd_sub_folder not in sys.path:
        sys.path.insert(0, cmd_sub_folder)


def run_util(util):
    this_path = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
    cmd_sub_folder = os.path.realpath(os.path.abspath(os.path.join(this_path, "bin")))
    cmd = os.path.join(cmd_sub_folder, 'elevate')
    try :
        call([cmd, '-wait', util])
    except Exception as e:
        print('Can not clear connections : ', e)

def get_path():
    this_path = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
    return os.path.realpath(os.path.abspath(this_path))


def get_path_root():
    current = get_path()
    root = os.path.dirname(current)
    return root



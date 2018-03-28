__author__ = 'david.hewitt'

import shutil
import os
import sys
import inspect
from subprocess import Popen

# todo: work up to adding iPython to the tutorial which would reduce the need for these utils


def fix_path(src_path, destination_path):
    if os.path.dirname(destination_path) == '':
        return os.path.join(os.path.dirname(src_path), destination_path)
    else:
        return destination_path


def get_path():
    this_path = os.path.split(inspect.getfile(inspect.currentframe()))[0]
    return os.path.realpath(os.path.abspath(this_path))


def get_project_root():
    current = get_path()
    root = os.path.dirname(current)
    return root


def get_file_path(*args):
    """Take location of the projecy root and add subdirectories + filename"""
    root = get_project_root()
    return os.path.join(root, *args)


def pwd():
    """Find pythons current working directory"""
    return os.getcwd()


def cp(src_path, destination_path, *args):
    """Copy a file or tree"""
    destination_path = fix_path(src_path, destination_path)
    if 'r' in args:
        shutil.copytree(src_path, destination_path)
    else:
        shutil.copy(src_path, destination_path)


def mv(src_path, destination_path):
    """move a file or tree"""
    destination_path = fix_path(src_path, destination_path)
    shutil.move(src_path, destination_path)


def rm(target_path, *args):
    """delete a file or a tree - add 'r'  as in rm( path,'r') to remove a tree"""
    if 'r' in args:
        shutil.rmtree(target_path)
    else:
        os.remove(target_path)


def edit(form_snap):
    """open a file in notepad"""
    Popen(["notepad", form_snap])


def ls(*args):
    """list the contents of a range of directories"""
    if not args:
        args = ['.']

    result = []
    for target_dir in args:
        result.append(os.listdir(target_dir))

    return result
'''
Random utilities that are used across many legendary modules.
'''

# core libraries
import errno
import importlib
import logging
import os

# packages already loaded
_LOADED_PACKAGES = {}

def get_package_from_name(legendary_set):
    '''
    Given a legendary set name, import the package that holds all of its config,
    and return a reference to it.
    '''
    # skip if already loaded
    if legendary_set in _LOADED_PACKAGES:
        return _LOADED_PACKAGES[legendary_set]

    # load it
    spec = importlib.util.find_spec(legendary_set)
    set_package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(set_package)
    _LOADED_PACKAGES[legendary_set] = set_package
    return _LOADED_PACKAGES[legendary_set]

def create_directory(directory):
    '''
    Create a directory, if necessary.
    '''
    # ensure directory exists
    try:
        os.makedirs(directory)
        logging.debug("Created the directory at: %s", directory)
    except OSError as os_error:
        # ignore if it already exists - this will be true 99% of the time
        if os_error.errno == errno.EEXIST:
            logging.debug("Directory '%s' already exists", directory)
        else:
            raise

def restore_default_rules():
    '''
    Restore the default rules from the package to the user-specific
    configuration directory.
    '''
    pass

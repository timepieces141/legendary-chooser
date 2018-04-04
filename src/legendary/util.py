'''
Random utilities that are used across many legendary modules.
'''

# core libraries
import errno
import json
import logging
import os
import shutil

# third party libraries
from appdirs import user_data_dir
import pkg_resources

# legendary libraries
from . exceptions import InitializationError

# constants
PACKAGED_LEGENDARY_SETS = ["buffy", "big_trouble"]
USER_DATA_DIR = user_data_dir("legendary", "Edward Petersen")
SETS_DIR = os.path.join(USER_DATA_DIR, "sets")

# for verbosity
LOGGING_LEVELS = {
    "0": logging.CRITICAL,
    "1": logging.ERROR,
    "2": logging.WARNING,
    "3": logging.INFO,
    "4": logging.DEBUG,
}

INITIALIZATION = '''** DO NOT MANUALLY REMOVE THIS FILE **

If this file does not exist when a legendary-chooser command is invoked, the
configuration files in the 'sets' directory will be ovewritten.
'''

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

def restore_file(legendary_set):
    '''
    Copy one of the packaged legendary set default configuration files to the
    user's set directory.
    '''
    # ensure the user's data directory and sets directory both exist
    try:
        create_directory(USER_DATA_DIR)
        create_directory(SETS_DIR)
    except OSError as os_error:
        if os_error.errno == errno.EACCES or os_error.errno == errno.EPERM:
            logging.warning("Directory '%s' is inaccessible because of a permissions error", os_error.filename)
            raise InitializationError("The directory '{}' is inaccessible because of a permissions error. Please " \
                                      "modify the ownership or permissions of the directory and try " \
                                      "again.".format(os_error.filename))
        else:
            raise

    # copy the file over
    try:
        src_config = pkg_resources.resource_filename("legendary",
                                                     os.path.join("data", "{}.config".format(legendary_set)))
        dst_config = os.path.join(SETS_DIR, "{}.config".format(legendary_set))
        shutil.copy(src_config, dst_config)
    except OSError as os_error:
        # if original files don't exist, alert user they can reinstalle
        # legendary chooser without fear of overwrititng their user data
        if os_error.errno == errno.ENOENT:
            logging.warning("Source configuration file '%s' for Legendary set '%s' does not exist!",
                            src_config,
                            legendary_set)
            raise InitializationError("The default configuration file for the Legendary set '{}' cannot be found in " \
                                      "the package installation. legendary-chooser can be reinstalled to solve this " \
                                      "problem without the risk of overwrititng any current user " \
                                      "data.".format(legendary_set))
        elif os_error.errno == errno.EACCES or os_error.errno == errno.EPERM:
            logging.warning("Destination configuraion file '%s' for Legendary set '%s' inaccessible because of a " \
                            "permissions error", dst_config, legendary_set)
            raise InitializationError("The user configuraion file for the Legendary set '{}', found at '{}' cannot " \
                                      "be overwritten because of a permissions error. Please modify the ownership or " \
                                      "permissions for this file and try again.".format(legendary_set, dst_config))
        else:
            raise

    logging.debug("Configuration file for Legendary set '%s' restored!", legendary_set)

def initialize(do_check=True):
    '''
    Check if we need initialization, and if so, create the user data directories
    and copy over the set config files.
    '''
    # check for our initialization file
    init_file = os.path.join(USER_DATA_DIR, ".initialized")
    if do_check and os.path.exists(init_file):
        logging.debug("Initialization file exists, skipping ...")
        return

    # loop through all of the legendary sets and copy over the config files
    logging.debug("Copying over Legendary set config files.")
    for legendary_set in PACKAGED_LEGENDARY_SETS:
        restore_file(legendary_set)

    # write our initialization file
    try:
        with open(init_file, "w") as init_ref:
            init_ref.write(INITIALIZATION)
            logging.debug("Initialization file written")
    except OSError as os_error:
        if os_error.errno == errno.EACCES or os_error.errno == errno.EPERM:
            error_msg = "The initialization file cannot be written because of a file system permission error."
            logging.error(error_msg)
            raise InitializationError(error_msg)
        else:
            raise

def available_sets():
    '''
    Look in the "sets" directory and return the names of all valid
    configurations.
    '''
    # start our list of available sets
    available = []

    # loop through the files
    for filename in os.listdir(SETS_DIR):

        # grab config files
        if filename.endswith(".config"):

            # load the json file
            with open(os.path.join(SETS_DIR, filename), "r") as set_ref:
                try:
                    json.load(set_ref)
                except json.JSONDecodeError:
                    logging.debug("'%s' is not a valid configuration file, skipping...", filename)
                    continue

            # if we get here, add the name to the list
            available.append(os.path.splitext(filename)[0])

        else:
            logging.debug("'%s' is not a appropriately named as a configuration file, skipping...", filename)

    return available

# # packages already loaded
# _LOADED_PACKAGES = {}

# def get_package_from_name(legendary_set):
#     '''
#     Given a legendary set name, import the package that holds all of its config,
#     and return a reference to it.
#     '''
#     # skip if already loaded
#     if legendary_set in _LOADED_PACKAGES:
#         return _LOADED_PACKAGES[legendary_set]

#     # load it
#     spec = importlib.util.find_spec(legendary_set)
#     set_package = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(set_package)
#     _LOADED_PACKAGES[legendary_set] = set_package
#     return _LOADED_PACKAGES[legendary_set]

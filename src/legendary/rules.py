'''
The rules module provides the functions used to validate the game configurations
against rule sets. Rules are stored in configuration files, so that house rules
and overrides can be kept over many executions.
'''

# core libraries
import errno
import json
import logging
import os
import sys

# third party libraries
from appdirs import user_data_dir

## This section of functions is used to validate game configurations.

def blacklisted_schemes(set_package, player_count):
    '''
    Retrieve the schemes that have been blacklisted by rules and house rules.
    '''
    # load the base rules in the legendary set, if neccesary
    _load_rules_configuration(set_package)

    # traverse the base rules to find the blacklisted schemes
    blacklisted = []
    config = getattr(set_package, "get_base_rules_config")()
    if "scheme" in config:
        if "player_count" in config["scheme"]:
            if str(player_count) in config["scheme"]["player_count"]:
                if "blacklisted" in config["scheme"]["player_count"][str(player_count)]:
                    for scheme_index in config["scheme"]["player_count"][str(player_count)]["blacklisted"]:
                        scheme = set_package.Schemes(scheme_index)
                        blacklisted.append(scheme)

    # load the house rules in the legendary set, if neccesary
    _load_rules_configuration(set_package, "house")

    # traverse the house rules to find the blacklisted schemes
    config = getattr(set_package, "get_house_rules_config")()
    if "scheme" in config:
        if "player_count" in config["scheme"]:
            if str(player_count) in config["scheme"]["player_count"]:
                if "blacklisted" in config["scheme"]["player_count"][str(player_count)]:
                    for scheme_index in config["scheme"]["player_count"][str(player_count)]["blacklisted"]:
                        scheme = set_package.Schemes(scheme_index)
                        blacklisted.append(scheme)

    return blacklisted

## This section is for loading the various rules configurations from file, and
#  in the case the file does not yet exist, loading a default configuration and
#  saving it to file.
#
#  A Note about the format of the rules configurations. The configuration is a
#  dictionary. Level one of the dictionary is one of "scheme," "mastermind,"
#  "villain," or "henchman" - the card *class* that validation methods are
#  looking to rule in or out. Level two is the parameter by which the card class
#  may be ruled out, such as player count. Level three is the *value* of the
#  parameter put forth in level two, such as "1" for player count. Level four is
#  the action to be taken, such as "blacklisting" a specific card group of the
#  card class defined in level one. In this instance, the value of level four
#  would be a list of integers, corresponding to the enum index for the card
#  class defined in level one. Another example of a level four "action" is
#  "count", the value of which will be a single integer, representing the number
#  of card groups to choose of the level one card class to complete the game
#  configuration.


def _load_rules_configuration(set_package, rules_type="base"):
    '''
    Load the rules configuration from disk. If the file does not exist, save the
    default config to disk after loading it for use here.
    '''
    package_name = set_package.__name__.split(".")[-1]
    # skip if already loaded
    if getattr(set_package, "get_{}_rules_config".format(rules_type))() is not None:
        logging.debug("'%s' %s rules configuration already loaded, skipping...", package_name.replace("_"," ").title(), rules_type)
        return

    # ensure data directory exists
    data_dir = user_data_dir("legendary", "Edward Petersen")
    try:
        os.makedirs(data_dir)
        logging.debug("Created the user data directory at: {}", data_dir)
    except OSError as os_error:
        # ignore if it already exists - this will be true 99% of the time
        if os_error.errno != errno.EEXIST:
            raise

    # attempt to load the rules config file - on error, load the default and
    # save it to file
    file_name = "{}.{}.rules.json".format(package_name, rules_type)
    rules_config_file = os.path.join(data_dir, file_name)
    try:
        with open(rules_config_file, "r") as rules_config_data_ref:
            getattr(set_package, "set_{}_rules_config".format(rules_type))(json.load(rules_config_data_ref))
            logging.info("'%s' %s rules configuration loaded", package_name.replace("_"," ").title(), rules_type)
    except FileNotFoundError:
        default_config = "DEFAULT_{}_RULES_CONFIG".format(rules_type.upper())
        getattr(set_package, "set_{}_rules_config".format(rules_type))(json.loads(getattr(set_package, default_config)))
        with open(rules_config_file, "w") as rules_config_data_ref:
            json.dump(getattr(set_package, "get_{}_rules_config".format(rules_type))(), rules_config_data_ref)
            logging.info("Created default '%s' %s rules configuration file", package_name.replace("_"," ").title(), rules_type)

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

# third party libraries
from appdirs import user_data_dir

## This section of functions is used to validate game configurations.

def count(scheme, scheme_package, player_count, card_class):
    '''
    Grab counts for the given card class from the rule sets.
    '''
    # get the count from the base rules
    base_rules = getattr(scheme_package, "BASE_RULES_CONFIG")
    house_rules = getattr(scheme_package, "HOUSE_RULES_CONFIG")
    base_count = base_rules["player_counts"][str(player_count)][card_class]

    for rules_set in [base_rules, house_rules]:
        try:
            base_count += rules_set["scheme_rules"][str(scheme.value)][card_class]["diff"]
        except KeyError:
            # it's ok if the rules don't include count diffs
            pass

    # if this brings us below zero, return zero (can't have negative cards in a
    # deck!)
    return base_count if base_count > 0 else 0

def scheme_blacklisted(scheme, scheme_package, player_count):
    '''
    Whether or not the given Scheme is blacklisted by player count in either
    rule set.
    '''
    # traverse the base rules to find the blacklisted schemes
    blacklisted = []
    for rules_set in ["BASE", "HOUSE"]:
        config = getattr(scheme_package, "{}_RULES_CONFIG".format(rules_set))
        try:
            for scheme_index in config["blacklisted_schemes"][str(player_count)]:
                blacklisted_scheme = scheme_package.Schemes(scheme_index)
                blacklisted.append(blacklisted_scheme)
        except KeyError:
            # it's ok if the rules don't include blacklisted schemes
            pass

    # return if scheme is in the blacklist
    return scheme in blacklisted

def required(scheme, scheme_package, component_type):
    '''
    Retrieve the set of "required" card groups of the given component type, for
    the given Scheme. This returns either a set of card groups for the given
    component type, or "None" if none are required. A requirement set (returned
    here) need only be a *subset* (but can be identitcal) to the configured
    component type to pass validation.
    '''
    # traverse the base rules to find required components
    required_set = set()
    for rules_set in ["BASE", "HOUSE"]:
        config = getattr(scheme_package, "{}_RULES_CONFIG".format(rules_set))
        try:
            for index in config["scheme_rules"][str(scheme.value)][component_type]["required"]:
                component = getattr(scheme_package, component_type.title())(index)
                required_set.update([component])
        except KeyError:
            # it's ok if the rules don't include requirements
            pass

    # return the list or None if it is empty
    return None if not required_set else required_set

def exclusive(scheme, scheme_package, component_type):
    '''
    Retrieve the set of "exclusive" card groups of the given component type, for
    the given Scheme. This returns either a set of card groups for the given
    component type, or "None" if none are required. An exclusive set (returned
    here) must be identical or a superset of the configured component type to
    pass validation.
    '''
    # traverse the base rules to find exclusive components
    exclusive_set = set()
    for rules_set in ["BASE", "HOUSE"]:
        config = getattr(scheme_package, "{}_RULES_CONFIG".format(rules_set))
        try:
            for index in config["scheme_rules"][str(scheme.value)][component_type]["exclusive"]:
                component = getattr(scheme_package, component_type.title())(index)
                exclusive_set.update([component])
        except KeyError:
            # it's ok if the rules don't include exclusive requirements
            pass

    # return the list or None if it is empty
    return None if not exclusive_set else exclusive_set

## This section is for loading the various rules configurations from file, and
#  in the case the file does not yet exist, loading a default configuration and
#  saving it to file.
#
#  A Note about the format of the rules configurations. The base rules are
#  divided into three section. In section one we find the "counts" of card
#  groups categorized by player count. For instance, in a 3-4 player game there
#  are 3 villain groups in the villain deck. In section two we find the
#  blacklisted schemes categorized by player count. For instance, some schemes
#  are not valid for solo play. And finally in section three, we find the
#  scheme-specific rules. The first level denotes the Scheme by number (the enum
#  index). The second level denotes the card group that has the special rule,
#  such as masterminds, villains, etc. And the third level has any of three
#  possible keywords:
#
#  "diff": [integer] Adds or subtracts to the count (as established in section
#  one)
#
#  "required": [list of enum indices] These item(s) are required, but not
#  exclusively - so as long as the list from the rules is a subset of the list
#  from the configuration, the game configuration will pass validation
#
#  "exclusive": [list of enum indices] The list of configured items in the game
#  configuration of the card type (defined in level two) must be a subset of
#  this list (all configured items must be in the list from the rules, and the
#  list *cannot* contain other items)
#

def _create_directory(directory):
    '''
    Create a directory, if necessary.
    '''
    # ensure directory exists
    try:
        os.makedirs(directory)
        logging.debug("Created the user data directory at: %s", directory)
    except OSError as os_error:
        # ignore if it already exists - this will be true 99% of the time
        if os_error.errno == errno.EEXIST:
            logging.debug("User data directory '%s' already exists", directory)
        else:
            raise

def load_rules_configuration(set_package, rules_type="base"):
    '''
    Load the rules configuration from disk. If the file does not exist, save the
    default config to disk after loading it for use here.
    '''
    # package name
    package_name = set_package.__name__.split(".")[-1]

    # skip if already loaded
    if getattr(set_package, "{}_RULES_CONFIG".format(rules_type.upper())) is not None:
        logging.debug("'%s' %s rules configuration already loaded, skipping...",
                      package_name.replace("_", " ").title(),
                      rules_type)
        return

    # ensure the data directory exists
    data_dir = user_data_dir("legendary", "Edward Petersen")
    _create_directory(data_dir)

    # attempt to load the rules config file - on error, load the default and
    # save it to file
    file_name = "{}.{}.rules.json".format(package_name, rules_type)
    rules_config_file = os.path.join(data_dir, file_name)
    try:
        with open(rules_config_file, "r") as rules_config_data_ref:
            setattr(set_package, "{}_RULES_CONFIG".format(rules_type.upper()), json.load(rules_config_data_ref))
            logging.info("'%s' %s rules configuration loaded", package_name.replace("_", " ").title(), rules_type)
    except FileNotFoundError:
        default_config = "DEFAULT_{}_RULES_CONFIG".format(rules_type.upper())
        setattr(set_package,
                "{}_RULES_CONFIG".format(rules_type.upper()),
                json.loads(getattr(set_package, default_config)))
        with open(rules_config_file, "w") as rules_config_data_ref:
            json.dump(getattr(set_package, "{}_RULES_CONFIG".format(rules_type.upper())), rules_config_data_ref)
            logging.info("Created default '%s' %s rules configuration file",
                         package_name.replace("_", " ").title(),
                         rules_type)

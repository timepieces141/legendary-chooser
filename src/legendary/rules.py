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

def masterminds_count(scheme, scheme_package, player_count):
    '''
    For the given scheme, and against the base and house rules, retrieve the
    number of Masterminds required for a valid setup.
    '''
    return _abstract_counts(scheme, scheme_package, player_count, "masterminds")

def villains_count(scheme, scheme_package, player_count):
    '''
    For the given scheme, and against the base and house rules, retrieve the
    number of Villains required for a valid setup.
    '''
    return _abstract_counts(scheme, scheme_package, player_count, "villains")

def henchmen_count(scheme, scheme_package, player_count):
    '''
    For the given scheme, and against the base and house rules, retrieve the
    number of Henchmen required for a valid setup.
    '''
    return _abstract_counts(scheme, scheme_package, player_count, "henchmen")

def enforcers_count(scheme, scheme_package, player_count):
    '''
    For the given scheme, and against the base and house rules, retrieve the
    number of Villains for the Enforcer deck required for a valid setup.
    '''
    return _abstract_counts(scheme, scheme_package, player_count, "enforcers")

def heroes_in_villain_deck_count(scheme, scheme_package, player_count):
    '''
    For the given scheme, and against the base and house rules, retrieve the
    number of Heroes for the Villain deck required for a valid setup.
    '''
    return _abstract_counts(scheme, scheme_package, player_count, "heroes_in_villain_deck")

def heroes_count(scheme, scheme_package, player_count):
    '''
    For the given scheme, and against the base and house rules, retrieve the
    number of Heroes for the Hero deck required for a valid setup.
    '''
    return _abstract_counts(scheme, scheme_package, player_count, "heroes")

def _abstract_counts(scheme, scheme_package, player_count, card_class):
    '''
    Grab counts for the given card class from the rule sets.
    '''
    # load the base rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package)

    # get the count from the base rules
    base_rules = getattr(scheme_package, "get_base_rules_config")()
    base_count = base_rules["player_counts"][str(player_count)][card_class]

    # add any scheme-specific changes from the base rules
    if str(scheme.value) in base_rules["scheme_rules"]:
        if card_class in base_rules["scheme_rules"][str(scheme.value)]:
            if "diff" in base_rules["scheme_rules"][str(scheme.value)][card_class]:
                base_count += base_rules["scheme_rules"][str(scheme.value)][card_class]["diff"]

    # load the house rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package, "house")

    # add any scheme-specific changes from the house rules
    house_rules = getattr(scheme_package, "get_house_rules_config")()
    if "scheme_rules" in house_rules:
        if str(scheme.value) in house_rules["scheme_rules"]:
            if card_class in house_rules["scheme_rules"][str(scheme.value)]:
                if "diff" in house_rules["scheme_rules"][str(scheme.value)][card_class]:
                    base_count += house_rules["scheme_rules"][str(scheme.value)][card_class]["diff"]

    return base_count

def scheme_blacklisted(scheme, scheme_package, player_count):
    '''
    Whether or not the given Scheme is blacklisted by player count in either
    rule set.
    '''
    # load the base rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package)

    # traverse the base rules to find the blacklisted schemes
    blacklisted = []
    config = getattr(scheme_package, "get_base_rules_config")()
    if "blacklisted_schemes" in config:
        if str(player_count) in config["blacklisted_schemes"]:
            for scheme_index in config["blacklisted_schemes"][str(player_count)]:
                blacklisted_scheme = scheme_package.Schemes(scheme_index)
                blacklisted.append(blacklisted_scheme)

    # load the house rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package, "house")

    # traverse the house rules to find the blacklisted schemes
    config = getattr(scheme_package, "get_house_rules_config")()
    if "blacklisted_schemes" in config:
        if str(player_count) in config["blacklisted_schemes"]:
            for scheme_index in config["blacklisted_schemes"][str(player_count)]:
                blacklisted_scheme = scheme_package.Schemes(scheme_index)
                blacklisted.append(blacklisted_scheme)

    # return if scheme is in the blacklist
    return scheme in blacklisted

def required_masterminds(scheme, scheme_package):
    '''
    Retrieve the "required" Masterminds for the given Scheme. This returns
    either a set of Masterminds, or "None" if none are required. A requirement
    set (returned here) need only be a *subset* (but can be identitcal) to the
    configured masterminds to pass validation.
    '''
    # load the base rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package)

    # traverse the base rules to find required masterminds
    required = set()
    config = getattr(scheme_package, "get_base_rules_config")()
    if "scheme_rules" in config:
        if str(scheme.value) in config["scheme_rules"]:
            if "masterminds" in config["scheme_rules"][str(scheme.value)]:
                if "required" in config["scheme_rules"][str(scheme.value)]["masterminds"]:
                    for mastermind_index in config["scheme_rules"][str(scheme.value)]["masterminds"]["required"]:
                        mastermind = scheme_package.Masterminds(mastermind_index)
                        required.update([mastermind])

    # load the house rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package, "house")

    # traverse the house rules to find required masterminds (these trump the
    # base rules entirely, including removing the requirement by making the list
    # empty)
    config = getattr(scheme_package, "get_house_rules_config")()
    if "scheme_rules" in config:
        if str(scheme.value) in config["scheme_rules"]:
            if "masterminds" in config["scheme_rules"][str(scheme.value)]:
                if "required" in config["scheme_rules"][str(scheme.value)]["masterminds"]:
                    required = set()
                    for mastermind_index in config["scheme_rules"][str(scheme.value)]["masterminds"]["required"]:
                        mastermind = scheme_package.Masterminds(mastermind_index)
                        required.update([mastermind])

    # return the list or None if it is empty
    return None if len(required) == 0 else required

def exclusive_masterminds(scheme, scheme_package):
    '''
    Retrieve the "exclusive" Masterminds for the given Scheme. This returns
    either a set of Masterminds, or "None" if none are exclusively required. An
    exclusive set (returned here) must be identical or a superset of the
    configured masterminds to pass validation.
    '''
    # load the base rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package)

    # traverse the base rules to find exclusively required masterminds
    exclusive = set()
    config = getattr(scheme_package, "get_base_rules_config")()
    if "scheme_rules" in config:
        if str(scheme.value) in config["scheme_rules"]:
            if "masterminds" in config["scheme_rules"][str(scheme.value)]:
                if "exclusive" in config["scheme_rules"][str(scheme.value)]["masterminds"]:
                    for mastermind_index in config["scheme_rules"][str(scheme.value)]["masterminds"]["exclusive"]:
                        mastermind = scheme_package.Masterminds(mastermind_index)
                        exclusive.update([mastermind])

    # load the house rules in the legendary set, if neccesary
    _load_rules_configuration(scheme_package, "house")

    # traverse the house rules to find exclusively required masterminds (these
    # trump the base rules entirely, including removing the requirement by
    # making the list empty)
    config = getattr(scheme_package, "get_house_rules_config")()
    if "scheme_rules" in config:
        if str(scheme.value) in config["scheme_rules"]:
            if "masterminds" in config["scheme_rules"][str(scheme.value)]:
                if "exclusive" in config["scheme_rules"][str(scheme.value)]["masterminds"]:
                    exclusive = set()
                    for mastermind_index in config["scheme_rules"][str(scheme.value)]["masterminds"]["exclusive"]:
                        mastermind = scheme_package.Masterminds(mastermind_index)
                        exclusive.update([mastermind])

    # return the list or None if it is empty
    return None if len(exclusive) == 0 else exclusive







## This section is for loading the various rules configurations from file, and
#  in the case the file does not yet exist, loading a default configuration and
#  saving it to file.
#
#  A Note about the format of the rules configurations. TODO: Fill this in.
#
#  "exclusive" means that the list of configured items of that card type must be a
#  subset of the list (all configured items must be in the list from the rules,
#  and the list *cannot* contain other items)
#
#  "diff": adds or subtracts to the count
#
#  "required" means that the item(s) are required, but not exclusively - so as
#  long as the list from the rules is a subset of the list from the
#  configuration, the config will pass validation

def _load_rules_configuration(set_package, rules_type="base"):
    '''
    Load the rules configuration from disk. If the file does not exist, save the
    default config to disk after loading it for use here.
    '''
    # package name
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

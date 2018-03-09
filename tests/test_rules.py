'''
Tests for the legendary.rules module.
'''

# core libraries
import types
import json
import logging
import os

# third party libraries
from appdirs import user_data_dir

# testing imports
import pytest

# code under test
from legendary import rules

@pytest.fixture
def base_rules():
    '''
    Base rules dictionary as returned by a set-specific rules module.
    '''
    return {
        "player_counts": {
            "1": {
                "masterminds": 1
            }
        }
    }

@pytest.mark.parametrize("scheme_number,player_count,card_group,base_scheme_rules_section," \
                         "house_scheme_rules_section,count",
                         [
                             # base rules count, no base rules scheme_rules
                             # section, no house rules scheme_rules section
                             (4, 1, "masterminds", None, None, 1),

                             # base rules count, no base rules scheme_rules
                             # section, house rules, but not this scheme
                             (3, 1, "masterminds", None, {"4": {"masterminds": {"diff": -1}}}, 1),

                             # base rules count, no base rules scheme_rules
                             # section, house rules, this scheme, but not this
                             # card group
                             (4, 1, "masterminds", None, {"4": {"villains": {"diff": -1}}}, 1),

                             # base rules count, no base rules scheme_rules
                             # section, house rules, this scheme, this card
                             # group, but not diffed
                             (4, 1, "masterminds", None, {"4": {"masterminds": {"something": "else"}}}, 1),

                             # base rules count, no base rules scheme_rules
                             # section, diffed in house rules
                             (4, 1, "masterminds", None, {"4": {"masterminds": {"diff": 4}}}, 5),

                             # base rules count, base rules scheme_rules section,
                             # but not this scheme, no house rules scheme_rules
                             # section
                             (3, 1, "masterminds", {"4": {"masterminds": {"diff": -1}}}, None, 1),

                             # base rules count, base rules scheme_rules section,
                             # this scheme, but not this card group, no base
                             # rules scheme_rules section
                             (4, 1, "masterminds", {"4": {"villains": {"diff": -1}}}, None, 1),

                             # base rules count, house rules scheme_rules
                             # section, this scheme, this card group, but not
                             # diffed, no base rules scheme_rules section
                             (4, 1, "masterminds", {"4": {"masterminds": {"something": "else"}}}, None, 1),

                             # base rules count, diffed in base rules, no base
                             # rules scheme_rules section
                             (4, 1, "masterminds", {"4": {"masterminds": {"diff": 4}}}, None, 5),

                             # base rules count, diffed in base rules, diffed in
                             # house rules
                             (4, 1, "masterminds", {"4": {"masterminds": {"diff": 1}}},
                              {"4": {"masterminds": {"diff": 1}}}, 3),

                             # zero floor - base rules negative
                             (4, 1, "masterminds", {"4": {"masterminds": {"diff": -10}}}, None, 0),

                             # zero floor - house rules negative
                             (4, 1, "masterminds", None, {"4": {"masterminds": {"diff": -10}}}, 0),

                             # zero floor - base rules and house rules negative
                             (4, 1, "masterminds", {"4": {"masterminds": {"diff": -10}}},
                              {"4": {"masterminds": {"diff": -10}}}, 0)
                         ] # pylint: disable=too-many-arguments
                        )
def test_count(base_rules, card_group_enum, # pylint: disable=redefined-outer-name
               scheme_number, player_count, card_group, base_scheme_rules_section, house_scheme_rules_section, count):
    '''
    Test the function that checks how many of a given card type should be
    included in a game configuration for a given player count.
    '''
    # set the scheme's package, where the set-specific rules live
    if base_scheme_rules_section:
        base_rules["scheme_rules"] = base_scheme_rules_section
    house_rules = {}
    if house_scheme_rules_section:
        house_rules["scheme_rules"] = house_scheme_rules_section
    scheme_package = types.SimpleNamespace(BASE_RULES_CONFIG=base_rules,
                                           HOUSE_RULES_CONFIG=house_rules,
                                           Schemes=card_group_enum)

    # test
    assert count == rules.count(card_group_enum(scheme_number), scheme_package, player_count, card_group)

@pytest.mark.parametrize("base_blacklisted,house_blacklisted,outcome",
                         [
                             (None, None, False), # in neither
                             ([], None, False),   # empty in base, not in house
                             (None, [], False),   # empty in house, not in base
                             ([], [], False),     # empty in both
                             ([1], None, False),  # not blacklisted in base, not in house
                             ([1], [], False),    # not blacklisted in base, empty in house
                             (None, [1], False),  # not blacklisted in house, not in base
                             ([], [1], False),    # not blacklisted in house, empty in base
                             ([1], [1], False),   # not blacklisted in either
                             ([4], None, True),   # blacklisted in base, not in house
                             ([4], [], True),     # blacklisted in base, empty in house
                             ([4], [1], True),    # blacklisted in base, not blacklisted in house
                             (None, [4], True),   # blacklisted in house, not in base
                             ([], [4], True),     # blacklisted in house, empty in base
                             ([1], [4], True),    # blacklisted in house, not blacklisted in base
                             ([4], [4], True),    # blacklisted in both
                         ]
                        )
def test_scheme_blacklisted(base_rules, card_group_enum, # pylint: disable=redefined-outer-name
                            base_blacklisted, house_blacklisted, outcome):
    '''
    Test the function that checks if a scheme has been blacklisted in either
    base and/or house rules, for a given player count.
    '''
    # set the scheme's package, where the set-specific rules live
    if base_blacklisted:
        base_rules["blacklisted_schemes"] = {"1": base_blacklisted}
    house_rules = {}
    if house_blacklisted:
        house_rules["blacklisted_schemes"] = {"1": house_blacklisted}
    scheme_package = types.SimpleNamespace(BASE_RULES_CONFIG=base_rules,
                                           HOUSE_RULES_CONFIG=house_rules,
                                           Schemes=card_group_enum)

    # test
    assert outcome == rules.scheme_blacklisted(card_group_enum(4), scheme_package, 1)

@pytest.mark.parametrize("card_group,base_scheme_rules_section,house_scheme_rules_section,outcome",
                         [
                             # scheme not in base rules' scheme_rules section,
                             # no house rules scheme_rules section
                             ("masterminds", {"3": {"henchmen": {"required": [1]}}}, None, None),

                             # scheme from base rules' scheme_rules section,
                             # but not the card group, no house rules
                             # scheme_rules section
                             ("masterminds", {"4": {"henchmen": {"required": [1]}}}, None, None),

                             # scheme from base rules' scheme_rules section,
                             # but no required list in card group, no house
                             # rules scheme_rules section
                             ("masterminds", {"4": {"masterminds": {"something": "else"}}}, None, None),

                             # required cards for card group for scheme from
                             # base rules's scheme_rules section, no house rules
                             # scheme_rules section
                             ("masterminds", {"4": {"masterminds": {"required": [1, 3]}}}, None, [1, 3]),

                             # scheme not in base rules' scheme_rules section,
                             # scheme not in house rules' scheme_rules section
                             ("masterminds", {"3": {"henchmen": {"required": [1]}}},
                              {"2": {"henchmen": {"required": [1]}}}, None),

                             # scheme not in base rules' scheme_rules section,
                             # scheme from house rules' scheme_rules section,
                             # but not the card group
                             ("masterminds", {}, {"4": {"henchmen": {"required": [1]}}}, None),

                             # scheme not in base rules' scheme_rules section,
                             # scheme from house rules' scheme_rules section,
                             # but no required list in card group
                             ("masterminds", {}, {"4": {"masterminds": {"something": "else"}}}, None),

                             # scheme not in base rules' scheme_rules section,
                             # required cards for card group for scheme from
                             # house rules' scheme_rules section
                             ("masterminds", {}, {"4": {"masterminds": {"required": [2, 4]}}}, [2, 4]),

                             # scheme in both scheme_rules sections of base and
                             # house rules
                             ("masterminds", {"4": {"masterminds": {"required": [1, 3]}}},
                              {"4": {"masterminds": {"required": [2, 4]}}}, [1, 2, 3, 4]),

                         ] # pylint: disable=too-many-arguments
                        )
def test_required(base_rules, card_group_enum, # pylint: disable=redefined-outer-name
                  card_group, base_scheme_rules_section, house_scheme_rules_section, outcome):
    '''
    Test the required function, which parses the base and house rules for
    "required" cards/card groups for a given scheme of a given card class.
    Required cards/card groups are ones that are required, but are not the only
    cards/card groups that may be included in a game configuration.
    '''
    # set the scheme's package, where the set-specific rules live
    base_rules["scheme_rules"] = base_scheme_rules_section
    house_rules = {}
    if house_scheme_rules_section:
        house_rules["scheme_rules"] = house_scheme_rules_section
    scheme_package = types.SimpleNamespace(BASE_RULES_CONFIG=base_rules,
                                           HOUSE_RULES_CONFIG=house_rules,
                                           Schemes=card_group_enum,
                                           Masterminds=card_group_enum)

    # expand the outcome list, where appropriate
    if outcome:
        outcome = {card_group_enum(index) for index in outcome}

    # test
    assert outcome == rules.required(card_group_enum(4), scheme_package, card_group)

@pytest.mark.parametrize("card_group,base_scheme_rules_section,house_scheme_rules_section,outcome",
                         [
                             # scheme not in base rules' scheme_rules section,
                             # no house rules scheme_rules section
                             ("masterminds", {"3": {"henchmen": {"exclusive": [1]}}}, None, None),

                             # scheme from base rules' scheme_rules section,
                             # but not the card group, no house rules
                             # scheme_rules section
                             ("masterminds", {"4": {"henchmen": {"exclusive": [1]}}}, None, None),

                             # scheme from base rules' scheme_rules section,
                             # but no exclusive list in card group, no house
                             # rules scheme_rules section
                             ("masterminds", {"4": {"masterminds": {"something": "else"}}}, None, None),

                             # exclusive cards for card group for scheme from
                             # base rules's scheme_rules section, no house rules
                             # scheme_rules section
                             ("masterminds", {"4": {"masterminds": {"exclusive": [1, 3]}}}, None, [1, 3]),

                             # scheme not in base rules' scheme_rules section,
                             # scheme not in house rules' scheme_rules section
                             ("masterminds", {"3": {"henchmen": {"exclusive": [1]}}},
                              {"2": {"henchmen": {"exclusive": [1]}}}, None),

                             # scheme not in base rules' scheme_rules section,
                             # scheme from house rules' scheme_rules section,
                             # but not the card group
                             ("masterminds", {}, {"4": {"henchmen": {"exclusive": [1]}}}, None),

                             # scheme not in base rules' scheme_rules section,
                             # scheme from house rules' scheme_rules section,
                             # but no exclusive list in card group
                             ("masterminds", {}, {"4": {"masterminds": {"something": "else"}}}, None),

                             # scheme not in base rules' scheme_rules section,
                             # exclusive cards for card group for scheme from
                             # house rules' scheme_rules section
                             ("masterminds", {}, {"4": {"masterminds": {"exclusive": [2, 4]}}}, [2, 4]),

                             # scheme in both scheme_rules sections of base and
                             # house rules
                             ("masterminds", {"4": {"masterminds": {"exclusive": [1, 3]}}},
                              {"4": {"masterminds": {"exclusive": [2, 4]}}}, [1, 2, 3, 4]),

                         ] # pylint: disable=too-many-arguments
                        )
def test_exclusive(base_rules, card_group_enum, # pylint: disable=redefined-outer-name
                   card_group, base_scheme_rules_section, house_scheme_rules_section, outcome):
    '''
    Test the exclusive function, which parses the base and house rules for
    "exclusive" cards/card groups for a given scheme of a given card class.
    Exclusive cards/card groups are ones that are *exclusively* required - for
    the given card class, these values are the *only* values allowed in a valid
    game configuration.
    '''
    # set the scheme's package, where the set-specific rules live
    base_rules["scheme_rules"] = base_scheme_rules_section
    house_rules = {}
    if house_scheme_rules_section:
        house_rules["scheme_rules"] = house_scheme_rules_section
    scheme_package = types.SimpleNamespace(BASE_RULES_CONFIG=base_rules,
                                           HOUSE_RULES_CONFIG=house_rules,
                                           Schemes=card_group_enum,
                                           Masterminds=card_group_enum)

    # expand the outcome list, where appropriate
    if outcome:
        outcome = {card_group_enum(index) for index in outcome}

    # test
    assert outcome == rules.exclusive(card_group_enum(4), scheme_package, card_group)

def test_create_directory(fs, # pylint: disable=invalid-name, unused-argument
                          caplog):
    '''
    Test the _create_directory function where the target directory does not
    exist. Ensure that when it does exist, nothing bad happens.
    '''
    # call _create_data_directory when it does not exist, verify that it was
    # created in the fake filesystem
    data_dir = user_data_dir("legendary", "Edward Petersen")
    assert not os.path.exists(data_dir)
    caplog.set_level(logging.DEBUG)
    rules._create_directory(data_dir) # pylint: disable=protected-access
    assert "Created the user data directory at: {}".format(data_dir) in caplog.text
    assert os.path.exists(data_dir)

    # call it again now that the directory exists, to hit the exception (that
    # ignores it)
    rules._create_directory(data_dir) # pylint: disable=protected-access
    assert "User data directory '{}' already exists".format(data_dir) in caplog.text

def test_create_directory_no_permission(fs): # pylint: disable=invalid-name
    '''
    Test the _create_directory function where the target directory to create
    cannot be created for a reason *other* than that it already exists - here,
    specifically, we use bad permissions.
    '''
    # create the parent directory to the user data directory in the fake file
    # system, but with harsh permissions, so as to see the raised exception that
    # *isn't* EEXIST
    data_dir = user_data_dir("legendary", "Edward Petersen")
    parent_dir = os.path.dirname(data_dir)
    fs.CreateDirectory(parent_dir, 0o444)
    with pytest.raises(PermissionError):
        rules._create_directory(data_dir) # pylint: disable=protected-access

@pytest.mark.parametrize("rules_type", [("base"), ("house")])
def test_load_rules_configuration_already_loaded(caplog, rules_type):
    '''
    Test the load_rules_configuration function, expecting an immediate return
    because the rules configuration has already been loaded. Test we see the log
    say so.
    '''
    set_package = types.SimpleNamespace(BASE_RULES_CONFIG={"something": "something"},
                                        HOUSE_RULES_CONFIG={"something": "something"},
                                        __name__="legendary.foobar")

    # test
    caplog.set_level(logging.DEBUG)
    rules.load_rules_configuration(set_package, rules_type)
    assert "'Foobar' {} rules configuration already loaded, skipping...".format(rules_type) in caplog.text

@pytest.mark.parametrize("rules_type", [("base"), ("house")])
def test_load_rules_configuration_no_file(fs, # pylint: disable=invalid-name
                                          monkeypatch, caplog, rules_type):
    '''
    Test the load_rules_configuration function where the rules file does not yet
    exist. Ensure that the files has been saved as expected and that the content
    saved matches the content loaded into the exported config variable.
    '''
    set_package = types.SimpleNamespace(BASE_RULES_CONFIG=None,
                                        HOUSE_RULES_CONFIG=None,
                                        DEFAULT_BASE_RULES_CONFIG="{\"default\": \"rules\"}",
                                        DEFAULT_HOUSE_RULES_CONFIG="{\"default\": \"rules\"}",
                                        __name__="legendary.foobar")

    # patch create_directory function, we test that elsewhere
    monkeypatch.setattr(rules, "_create_directory", lambda directory: None)
    data_dir = user_data_dir("legendary", "Edward Petersen")
    fs.CreateDirectory(data_dir)

    # call the function and assert we traverse the path we are testing
    caplog.set_level(logging.DEBUG)
    rules.load_rules_configuration(set_package, rules_type)
    assert "Created default 'Foobar' {} rules configuration file".format(rules_type) in caplog.text

    # verify the file now exists, the config has been loaded, and the contents
    # of the file match
    rules_config_file = os.path.join(data_dir, "foobar.{}.rules.json".format(rules_type))
    assert os.path.exists(rules_config_file)
    with open(rules_config_file, "r") as rules_config_data_ref:
        assert (json.load(rules_config_data_ref) ==
                getattr(set_package, "{}_RULES_CONFIG".format(rules_type.upper())) ==
                {"default": "rules"})

@pytest.mark.parametrize("rules_type", [("base"), ("house")])
def test_load_rules_configuration_file_exists(fs, # pylint: disable=invalid-name
                                              monkeypatch, rules_type):
    '''
    Test the load_rules_configuration function where the rules config files
    *already* exists. Ensure that the config loaded into the exported rules
    variable is what is saved in a the file.
    '''
    set_package = types.SimpleNamespace(BASE_RULES_CONFIG=None,
                                        HOUSE_RULES_CONFIG=None,
                                        __name__="legendary.foobar")

    # patch create_directory function, we test that elsewhere
    monkeypatch.setattr(rules, "_create_directory", lambda directory: None)

    # create the rules file that will be loaded
    data_dir = user_data_dir("legendary", "Edward Petersen")
    rules_config_file = os.path.join(data_dir, "foobar.{}.rules.json".format(rules_type))
    contents = {"default": "rules"}
    fs.CreateFile(rules_config_file, contents=json.dumps(contents))

    # test that the config loaded from file is what saved to file in the
    # previous setup step
    assert getattr(set_package, "{}_RULES_CONFIG".format(rules_type.upper())) is None
    rules.load_rules_configuration(set_package, rules_type)
    assert getattr(set_package, "{}_RULES_CONFIG".format(rules_type.upper())) == contents

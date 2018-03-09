'''
Tests for the legendary.components module.
'''

# pylint: disable=protected-access

# core libraries
import copy
import logging
import types

# testing imports
import pytest

# code under test
from legendary import components

# legendary code
from legendary import rules, util
from legendary.exceptions import ConfigurationError, ValidationError

# the different card classes held in the villain deck
VILLAIN_DECK = ["villains", "henchmen", "heroes_in_villain_deck"]

@pytest.fixture
def villain_deck(monkeypatch, card_group_enum):
    '''
    A fixture for providing a vanilla VillainDeck constructed. It uses the
    card_group_enum fixture to provide a mock Scheme.
    '''
    monkeypatch.setattr(util, "get_package_from_name", lambda scheme_set_name: 0)
    monkeypatch.setattr(rules, "count", lambda scheme, scheme_package, player_count, card_class: 1)
    scheme = card_group_enum(4)
    return components.VillainDeck(scheme, scheme.__module__, 1)

@pytest.fixture
def game_config(monkeypatch, card_group_enum):
    '''
    A vanilla GameConfiguration object.
    '''
    # patch the calls out to util and rules
    monkeypatch.setattr(util, "get_package_from_name", lambda scheme_set_name: 0)
    monkeypatch.setattr(rules, "count", lambda scheme, scheme_package, player_count, card_class: 1)
    return components.GameConfiguration(card_group_enum(4), "foobars_package")

@pytest.fixture
def game_config_always_leads_off(monkeypatch, card_group_enum):
    '''
    A vanilla GameConfiguration object with the "always leads" function turned
    off.
    '''
    # patch the calls out to util and rules
    monkeypatch.setattr(util, "get_package_from_name", lambda scheme_set_name: 0)
    monkeypatch.setattr(rules, "count", lambda scheme, scheme_package, player_count, card_class: 1)
    return components.GameConfiguration(card_group_enum(4), "foobars_package", always_leads=False)

@pytest.fixture
def bigger_game_config(monkeypatch, card_group_enum):
    '''
    A vanilla GameConfiguration object, but this time with a higher count (2)
    for all the components.
    '''
    # patch the calls out to util and rules
    monkeypatch.setattr(util, "get_package_from_name", lambda scheme_set_name: 0)
    monkeypatch.setattr(rules, "count", lambda scheme, scheme_package, player_count, card_class: 2)
    return components.GameConfiguration(card_group_enum(4), "foobars_package")

def test_configuration_component(card_group_enum):
    '''
    Test the ConfigurationComponent object.
    '''
    # test construction and append method under normal circumstances
    comp = components.ConfigurationComponent("Masterminds", "masterminds", 1)
    assert comp.card_class == "Masterminds"
    assert comp.card_class_use == "masterminds"
    assert comp.count == 1
    assert comp.card_groups == {}
    comp.append(card_group_enum(1), "ones_package")
    assert comp.card_groups == {card_group_enum(1): "ones_package"}
    comp.append(card_group_enum(1), "ones_package")
    assert comp.card_groups == {card_group_enum(1): "ones_package"}

    # if compared to something other than a ConfigurationComponent
    assert comp.__eq__("foobar") == NotImplemented

    # if compared to another component with different initializing attributes
    # (card_groups is tested through the game config)
    assert not comp.__eq__(components.ConfigurationComponent("Foobar", "masterminds", 1))
    assert not comp.__eq__(components.ConfigurationComponent("Masterminds", "foobar", 1))
    assert not comp.__eq__(components.ConfigurationComponent("Masterminds", "masterminds", 2))

    # test adding too many card groups
    with pytest.raises(ConfigurationError, message="Too many 'Masterminds' added to this configuration"):
        comp.append(card_group_enum(2), "twos_package")

def test_villaindeck_construction(villain_deck): # pylint: disable=redefined-outer-name
    '''
    Test the construction of a VillainDeck object - this holds nothing and has
    been pegged at needing zero items.
    '''
    for card_type in VILLAIN_DECK:
        component = getattr(villain_deck, card_type)
        assert getattr(component, "card_groups") == {}
        assert getattr(component, "count") == 1

    # if compared to something other than a VillainDeck
    assert villain_deck.__eq__("foobar") == NotImplemented

def test_gameconfig_construction(game_config, game_config_always_leads_off, card_group_enum): # pylint: disable=redefined-outer-name
    '''
    Test the construction of a GameConfiguration object.
    '''
    # check basic members filled at construction
    assert game_config.scheme == card_group_enum(4)
    assert game_config.always_leads
    assert game_config.player_count == 1
    assert game_config_always_leads_off.scheme == card_group_enum(4)
    assert not game_config_always_leads_off.always_leads
    assert game_config_always_leads_off.player_count == 1

@pytest.mark.parametrize("member_to_test,card_class",
                         [
                             ("masterminds", "Masterminds"),
                             ("villains", "Villains"),
                             ("henchmen", "Henchmen"),
                             ("heroes_in_villain_deck", "Heroes"),
                             ("enforcers", "Villains"),
                             (False, None)
                         ]
                        )
def test_next_game_component(game_config, # pylint: disable=redefined-outer-name
                             card_group_enum, member_to_test, card_class):
    '''
    Test the next_game_component method as game configuration moves through the
    stages of being filled.
    '''
    # load up the game config to point we are testing
    members = ["masterminds"] + VILLAIN_DECK + ["enforcers"]
    for member in members:
        if member == member_to_test:
            break
        if member in VILLAIN_DECK:
            component = getattr(game_config.villain_deck, member)
        else:
            component = getattr(game_config, member)
        component.append(card_group_enum(4), "the_enums_package")

    # test
    if member_to_test:
        assert game_config.next_game_component() == components.ConfigurationComponent(card_class, member_to_test, 1)
    else:
        assert not game_config.next_game_component()

@pytest.mark.parametrize("member_to_test",
                         [
                             ("masterminds"),
                             ("villains"),
                             ("henchmen"),
                             ("heroes_in_villain_deck"),
                             ("enforcers"),
                             (False)
                         ]
                        )
def test_next_game_component_multiples(bigger_game_config, # pylint: disable=redefined-outer-name
                                       card_group_enum, member_to_test):
    '''
    Test the next_game_component method as game configuration moves through the
    stages of being filled - this time expect that each component must be filled
    twice.
    '''
    # load up the game config to point we are testing
    members = ["masterminds"] + VILLAIN_DECK + ["enforcers"]
    for member in members:
        if member == member_to_test:
            break
        if member in VILLAIN_DECK:
            component = getattr(bigger_game_config.villain_deck, member)
        else:
            component = getattr(bigger_game_config, member)
        component.append(card_group_enum(3), "the_enums_package")
        assert bigger_game_config.next_game_component() == component
        component.append(card_group_enum(4), "the_enums_package")

    # test
    if member_to_test:
        if member_to_test in VILLAIN_DECK:
            assert bigger_game_config.next_game_component() == getattr(bigger_game_config.villain_deck, member_to_test)
        else:
            assert bigger_game_config.next_game_component() == getattr(bigger_game_config, member_to_test)
    else:
        assert not bigger_game_config.next_game_component()

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_required_nothing_required(game_config, # pylint: disable=redefined-outer-name
                                         monkeypatch, component_type):
    '''
    Test the _check_required method where nothing is required for the given
    component type (expect a return True). It doesn't matter that there is
    nothing loaded into game config for the component type we test with, since
    this method takes the set to check against (doesn't check the component
    dict). This is true of all the tests for _check_required and
    _check_exclusive.
    '''
    # monkeypatch the call to rules.required to return an empty set
    monkeypatch.setattr(rules, "required", lambda scheme, scheme_package, component_type: None)

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched required method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    # test that the set provided meets the requirement (since nothing is
    # required)
    assert game_config._check_required(components.ConfigurationComponent(component_type.title(), component_type, 1))

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_required_met_exactly(game_config, # pylint: disable=redefined-outer-name
                                    monkeypatch, card_group_enum, component_type):
    '''
    Test the _check_required method where something is required and the current
    configuration meets the requirement exactly (expect a return True). Meaning,
    the set of what is configured is exactly the set of what is required.
    '''
    # monkeypatch the call to rules.required to return a specific set set
    monkeypatch.setattr(rules, "required",
                        lambda scheme, scheme_package, component_type: {card_group_enum(1), card_group_enum(3)})

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched required method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    # test that the set provided meets the requirement exactly
    component = components.ConfigurationComponent(component_type.title(), component_type, 2)
    component.append(card_group_enum(1), "package")
    component.append(card_group_enum(3), "package")
    assert game_config._check_required(component)

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_required_met(game_config, # pylint: disable=redefined-outer-name
                            monkeypatch, card_group_enum, component_type):
    '''
    Test the _check_required method where something is required and the current
    configuration meets the requirement, even if it surpasses the requirement
    (expect a return True). Meaning, the set of what is configured is *more*
    than the set of what is required.
    '''
    # monkeypatch the call to rules.required to return a specific set set
    monkeypatch.setattr(rules, "required",
                        lambda scheme, scheme_package, component_type: {card_group_enum(1), card_group_enum(2)})

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched required method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    # test that the set provided meets the requirement, even if it surpasses it
    component_one = components.ConfigurationComponent(component_type.title(), component_type, 3)
    component_one.append(card_group_enum(1), "package")
    component_one.append(card_group_enum(2), "package")
    component_two = copy.deepcopy(component_one)
    component_one.append(card_group_enum(3), "package")
    component_two.append(card_group_enum(4), "package")
    assert game_config._check_required(component_one)
    assert game_config._check_required(component_two)

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_required_not_met(game_config, # pylint: disable=redefined-outer-name
                                monkeypatch, card_group_enum, component_type):
    '''
    Test the _check_required method where something is required and the current
    configuration does *not* meet the requirement (expect a return False).
    Meaning, the set of what is configured is *less* than the set of what is
    required.
    '''
    # monkeypatch the call to rules.required to return a specific set set
    monkeypatch.setattr(rules, "required",
                        lambda scheme, scheme_package, component_type: {card_group_enum(1), card_group_enum(3)})

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched required method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    ## test that the set provided does NOT include the required items

    # empty set
    component = components.ConfigurationComponent(component_type.title(), component_type, 2)
    assert not game_config._check_required(component)

    # only one of the two
    component.append(card_group_enum(1), "package")
    assert not game_config._check_required(component)
    dup_comp = copy.deepcopy(component)
    component.append(card_group_enum(2), "package")
    assert not game_config._check_required(component)
    dup_comp.append(card_group_enum(4), "package")
    assert not game_config._check_required(dup_comp)
    component = components.ConfigurationComponent(component_type.title(), component_type, 2)
    component.append(card_group_enum(3), "package")
    dup_comp = copy.deepcopy(component)
    component.append(card_group_enum(2), "package")
    assert not game_config._check_required(component)
    dup_comp.append(card_group_enum(4), "package")
    assert not game_config._check_required(dup_comp)

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_exclusive_nothing_required(game_config, # pylint: disable=redefined-outer-name
                                          monkeypatch, component_type):
    '''
    Test the _check_exclusive method where nothing is required for the given
    component type (expect a return True).
    '''
    # monkeypatch the call to rules.exclusive to return an empty set
    monkeypatch.setattr(rules, "exclusive", lambda scheme, scheme_package, component_type: None)

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched exclusive method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    # test that the set provided meets the requirement (since nothing is
    # required)
    assert game_config._check_exclusive(components.ConfigurationComponent(component_type.title(), component_type, 1))

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_exclusive_met_exactly(game_config, # pylint: disable=redefined-outer-name
                                     monkeypatch, card_group_enum, component_type):
    '''
    Test the _check_exclusive method where something is required and the current
    configuration meets the requirement exactly, as it must (expect a return
    True). Meaning, the set of what is configured is exactly the set of what is
    required.
    '''
    # monkeypatch the call to rules.required to return a specific set set
    monkeypatch.setattr(rules, "exclusive",
                        lambda scheme, scheme_package, component_type: {card_group_enum(1), card_group_enum(3)})

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched exclusive method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    # test that the set provided meets the requirement exactly
    component = components.ConfigurationComponent(component_type.title(), component_type, 2)
    component.append(card_group_enum(1), "package")
    component.append(card_group_enum(3), "package")
    assert game_config._check_exclusive(component)

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_exclusive_met(game_config, # pylint: disable=redefined-outer-name
                             monkeypatch, card_group_enum, component_type):
    '''
    Test the _check_exclusive method where something is required and the current
    configuration meets the requirement, even if doesn't include all of the
    exclusive set (return True).
    '''
    # monkeypatch the call to rules.required to return a specific set set
    monkeypatch.setattr(rules, "exclusive",
                        lambda scheme, scheme_package, component_type: {card_group_enum(1), card_group_enum(3)})

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched exclusive method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    # test that the set provided meets the requirement, even if not fully
    component_one = components.ConfigurationComponent(component_type.title(), component_type, 1)
    component_one.append(card_group_enum(1), "package")
    assert game_config._check_exclusive(component_one)

    component_two = components.ConfigurationComponent(component_type.title(), component_type, 1)
    component_two.append(card_group_enum(3), "package")
    assert game_config._check_exclusive(component_two)

@pytest.mark.parametrize("component_type",
                         [("masterminds"), ("villains"), ("henchmen"), ("heroes_in_villain_deck"), ("enforcers")])
def test_check_exclusive_not_met(game_config, # pylint: disable=redefined-outer-name
                                 monkeypatch, card_group_enum, component_type):
    '''
    Test the _check_exclusive method where something is required, bu the current
    configuration provides too many of the component type (return False).
    '''
    # monkeypatch the call to rules.required to return a specific set set
    monkeypatch.setattr(rules, "exclusive",
                        lambda scheme, scheme_package, component_type: {card_group_enum(1), card_group_enum(3)})

    # monkeypatch the call to util.get_package_from_name, it can return anything
    # - it's just fed into the monkeypatched exclusive method call above
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: "foobar")

    ## test that the set provided does *not* meet the requirement

    # empty set
    component_one = components.ConfigurationComponent(component_type.title(), component_type, 3)
    assert not game_config._check_exclusive(component_one)

    # only one of the two
    component_one.append(card_group_enum(1), "package")
    component_two = copy.deepcopy(component_one)
    component_one.append(card_group_enum(2), "package")
    assert not game_config._check_exclusive(component_one)
    component_one.append(card_group_enum(3), "package")
    assert not game_config._check_exclusive(component_one)

    component_two.append(card_group_enum(3), "package")
    assert game_config._check_exclusive(component_two)
    component_two.append(card_group_enum(4), "package")
    assert not game_config._check_exclusive(component_one)

    component_three = components.ConfigurationComponent(component_type.title(), component_type, 2)
    component_three.append(card_group_enum(3), "package")
    component_four = copy.deepcopy(component_three)
    component_three.append(card_group_enum(2), "package")
    assert not game_config._check_exclusive(component_three)
    component_four.append(card_group_enum(4), "package")
    assert not game_config._check_exclusive(component_four)

def test_simple_validate(game_config, # pylint: disable=redefined-outer-name
                         monkeypatch, card_group_enum):
    '''
    Test the _simple_validate method, which just encapsulates calling both the
    _check_required and _check_exclusive methods in one atomic procedure.
    '''
    # construct a generic component to be validated
    component = components.ConfigurationComponent("Foobar", "foobar", 1)

    # test for the premature validation
    with pytest.raises(ValidationError,
                       message="The component '{}' was validated before it was " \
                               "complete".format(component.card_class_use.replace("_", " "))):
        game_config._simple_validate(component)

    # now fill it
    component.append(card_group_enum(4), "foobar")

    # monkeypatch the _check_required to return False and check this fails
    # simple validation, even if _check_exclusive would otherwise return True
    monkeypatch.setattr(game_config, "_check_exclusive", lambda component: True)
    monkeypatch.setattr(game_config, "_check_required", lambda component: False)
    assert not game_config._simple_validate(component)

    # monkeypatch the _check_exclusive to return False and check this fails
    # simple validation, even if _check_required would otherwise return True
    monkeypatch.setattr(game_config, "_check_required", lambda component: True)
    monkeypatch.setattr(game_config, "_check_exclusive", lambda component: False)
    assert not game_config._simple_validate(component)

    # both must return True in order for simple validation to pass
    monkeypatch.setattr(game_config, "_check_required", lambda component: True)
    monkeypatch.setattr(game_config, "_check_exclusive", lambda component: True)
    assert game_config._simple_validate(component)

def test_validate_villains_always_leads_off(game_config_always_leads_off, # pylint: disable=redefined-outer-name
                                            monkeypatch):
    '''
    Test the _validate_villains method, which has to deal with the "always
    leads" mechanism. This test is for when the "always leads" function is
    turned off (becomes a conduit to _simple_validate).
    '''
    # if always leads is off, it dishes off to _simple_validate, which we've
    # already tested
    monkeypatch.setattr(game_config_always_leads_off, "_simple_validate", lambda component: True)
    assert game_config_always_leads_off._validate_villains()
    monkeypatch.setattr(game_config_always_leads_off, "_simple_validate", lambda component: False)
    assert not game_config_always_leads_off._validate_villains()

@pytest.mark.parametrize("masterminds,villains,outcome",
                         [
                             ([4], [4], True), # configured with 1 mastermind, 1 villain required by count
                             ([4], [3], False), # configured with 1 mastermind, 1 villain required by count
                             ([4], [3, 4], True), # configured with 1 mastermind, 2 villains required by count
                             ([4], [2, 3], False), # configured with 1 mastermind, 2 villains required by count
                             ([3, 4], [3], True), # configured with 2 masterminds, but only 1 villain by count required
                             ([3, 4], [4], True), # configured with 2 masterminds, but only 1 villain by count required
                             ([3, 4], [2], False), # configured with 2 masterminds, but only 1 villain by count required
                             ([3, 4], [3, 4], True), # confiugred with 2 masterminds, 2 required villains by count
                             ([3, 4], [2, 4], False), # confiugred with 2 masterminds, 2 required villains by count
                             ([3, 4], [1, 2], False), # confiugred with 2 masterminds, 2 required villains by count
                             ([3, 4], [2, 3, 4], True), # configured with 2 masterminds, 3 required villains by count
                             ([3, 4], [1, 2, 4], False) # configured with 2 masterminds, 3 required villains by count
                         ] # pylint: disable=too-many-arguments
                        )
def test_validate_villains_always_leads(game_config, # pylint: disable=redefined-outer-name
                                        monkeypatch, card_group_enum, masterminds, villains, outcome):
    '''
    Test the _validate_villains method, which has to deal with the "always
    leads" mechanism. This test is for when the "always leads" function is
    turned on and verifies, regardless of mastermind count or villain count,
    that we get the expected result when certain villains are present or absent.
    '''
    # ensure _simple_validate will always return True, even if we never hit it
    monkeypatch.setattr(game_config, "_simple_validate", lambda component: True)

    # overwrite the masterminds ConfigurationComponent with the right count
    game_config._masterminds = components.ConfigurationComponent("Masterminds", "masterminds", len(masterminds))

    # overwrite the villains ConfigurationComponent with the right count
    game_config._villain_deck._villains = components.ConfigurationComponent("Villains", "villains", len(villains))

    # ensure _simple_validate will always return True, even if we never hit it
    monkeypatch.setattr(game_config, "_simple_validate", lambda component: True)

    # add the mastermind(s) to the game config
    mastermind_package = types.SimpleNamespace(Villains=card_group_enum)
    monkeypatch.setattr(util, "get_package_from_name", lambda legendary_set: mastermind_package)
    for mastermind_index in masterminds:
        game_config._masterminds.append(card_group_enum(mastermind_index), mastermind_package)

    # add the villain(s) - package doesn't matter, but what the heck
    for villain_index in villains:
        game_config._villain_deck.villains.append(card_group_enum(villain_index), mastermind_package)

    # and test we have met the requirement
    assert outcome == game_config._validate_villains()

def test_validate_scheme(game_config, # pylint: disable=redefined-outer-name
                         monkeypatch, caplog):
    '''
    Test the _validate_scheme method, which in turn (for now) just checks if the
    configured scheme is blacklisted (which we test in the test_rules file).
    '''
    # nothing blacklisted
    monkeypatch.setattr(rules, "scheme_blacklisted", lambda scheme, scheme_package, player_count: False)
    assert game_config._validate_scheme()

    # blacklisted
    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(rules, "scheme_blacklisted", lambda scheme, scheme_package, player_count: True)
    assert not game_config._validate_scheme()
    assert "Config with blacklisted scheme \"Foobar\" marked as invalid" in caplog.text

@pytest.mark.parametrize("deck_name,component_name,validation_method",
                         [
                             (None, "scheme", "_validate_scheme"), # validate scheme
                             (None, "_masterminds", None), # validate masterminds
                             ("_villain_deck", "villains", "_validate_villains"), # validate villains
                             ("_villain_deck", "henchmen", None), # validate henchmen
                             ("_villain_deck", "heroes_in_villain_deck", None), # validate heroes in villain deck
                             (None, "_enforcers", None) # validate enforcers
                         ] # pylint: disable=too-many-arguments
                        )
def test_validate(game_config, # pylint: disable=redefined-outer-name
                  monkeypatch, card_group_enum, deck_name, component_name, validation_method):
    '''
    Test the validation method. This merely tests the cascading validation as
    items are available in the configuration. All of the tests that validation
    is happening correctly are above and in the test_rules file.
    '''
    # validate the scheme
    if component_name == "scheme":
        monkeypatch.setattr(game_config, validation_method, lambda: False)
        assert not game_config.validate()
        monkeypatch.setattr(game_config, validation_method, lambda: True)
        assert game_config.validate()
        return

    # fill the component so it can be validated
    if deck_name:
        component = getattr(getattr(game_config, deck_name), component_name)
    else:
        component = getattr(game_config, component_name)
    component.append(card_group_enum(4), "foobar")

    # patch the appropriate sub-validation method
    if not validation_method:
        monkeypatch.setattr(game_config, "_simple_validate", lambda component: False)
        assert not game_config.validate()
        monkeypatch.setattr(game_config, "_simple_validate", lambda component: True)
        assert game_config.validate()
    else:
        monkeypatch.setattr(game_config, validation_method, lambda: False)
        assert not game_config.validate()
        monkeypatch.setattr(game_config, validation_method, lambda: True)
        assert game_config.validate()

def test_game_config_string_representation(game_config, # pylint: disable=redefined-outer-name
                                           card_group_enum):
    '''
    Test the string representation of a game config.
    '''
    str_representation = "\nGame Configuration\n\tScheme: {}\n".format(card_group_enum(4).name)
    assert game_config.__str__() == str_representation

    # add masterminds
    str_representation += "\tMasterminds: {}\n".format(card_group_enum(1).name)
    game_config._masterminds.append(card_group_enum(1), "package_name")
    assert game_config.__str__() == str_representation

    # add villains
    str_representation += "\tVillain Deck:\n"
    str_representation += "\t\tVillains: {}\n".format(card_group_enum(2).name)
    game_config._villain_deck.villains.append(card_group_enum(2), "package_name")
    assert game_config.__str__() == str_representation

    # add henchmen
    str_representation += "\t\tHenchmen: {}\n".format(card_group_enum(3).name)
    game_config._villain_deck.henchmen.append(card_group_enum(3), "package_name")
    assert game_config.__str__() == str_representation

    # add heroes in the villain deck
    str_representation += "\t\tHeroes: {}\n".format(card_group_enum(1).name)
    game_config._villain_deck.heroes_in_villain_deck.append(card_group_enum(1), "package_name")
    assert game_config.__str__() == str_representation

    # add enforcers
    str_representation += "\tEnforcer Deck:\n"
    str_representation += "\t\tVillains: {}\n".format(card_group_enum(1).name)
    game_config._enforcers.append(card_group_enum(1), "package_name")
    assert game_config.__str__() == str_representation

def test_game_config_representation(game_config, # pylint: disable=redefined-outer-name
                                    card_group_enum):
    '''
    Test the representation of the game config.
    '''
    representation = "<GameConfiguration Scheme=\"Foobar\""
    assert repr(game_config) == representation + ">"

    # add mastermind
    representation += " Mastermind=\"{}\"".format(card_group_enum(1).name)
    game_config._masterminds.append(card_group_enum(1), "package_name")
    assert repr(game_config) == representation + ">"

    # add villains
    representation += " Villain=\"{}\"".format(card_group_enum(2).name)
    game_config._villain_deck.villains.append(card_group_enum(2), "package_name")
    assert repr(game_config) == representation + ">"

    # add henchmen
    representation += " Henchman=\"{}\"".format(card_group_enum(3).name)
    game_config._villain_deck.henchmen.append(card_group_enum(3), "package_name")
    assert repr(game_config) == representation + ">"

    # add hero for villain deck
    representation += " Hero_in_Villain_Deck=\"{}\"".format(card_group_enum(1).name)
    game_config._villain_deck.heroes_in_villain_deck.append(card_group_enum(1), "package_name")
    assert repr(game_config) == representation + ">"

    # add villain to enforcer deck
    representation += " Enforcer=\"{}\"".format(card_group_enum(2).name)
    game_config._enforcers.append(card_group_enum(2), "package_name")
    assert repr(game_config) == representation + ">"

def test_game_config_equals(game_config, # pylint: disable=redefined-outer-name
                            card_group_enum):
    '''
    Test the __eq__ method of the game config.
    '''
    # if compared to something other than a GameConfiguration
    assert game_config.__eq__("foobar") == NotImplemented

    # compare configs with masterminds
    alt_config = copy.deepcopy(game_config)
    game_config._masterminds.append(card_group_enum(1), "foobar")
    dup_config = copy.deepcopy(game_config)
    assert game_config.__eq__(dup_config)
    assert dup_config.__eq__(game_config)
    alt_config._masterminds.append(card_group_enum(2), "foobar")
    assert not game_config.__eq__(alt_config)
    assert not alt_config.__eq__(game_config)

    # compare configs with components from the villain deck
    for card_class in VILLAIN_DECK:
        # copy before and after adding the card group
        alt_config = copy.deepcopy(game_config)
        getattr(game_config.villain_deck, card_class).append(card_group_enum(1), "foobar")
        dup_config = copy.deepcopy(game_config)

        # dup should return equal
        assert game_config.__eq__(dup_config)
        assert dup_config.__eq__(game_config)

        # update alt config with different card group
        getattr(alt_config.villain_deck, card_class).append(card_group_enum(2), "foobar")

        # alt should return not equal
        assert not game_config.__eq__(alt_config)
        assert not alt_config.__eq__(game_config)

    # compare configs with enforcers
    alt_config = copy.deepcopy(game_config)
    game_config._enforcers.append(card_group_enum(1), "foobar")
    dup_config = copy.deepcopy(game_config)
    assert game_config.__eq__(dup_config)
    assert dup_config.__eq__(game_config)
    alt_config._enforcers.append(card_group_enum(2), "foobar")
    assert not game_config.__eq__(alt_config)
    assert not alt_config.__eq__(game_config)

def test_game_config_hash(game_config, # pylint: disable=redefined-outer-name
                          card_group_enum):
    '''
    Test the __hash__ method of the game config.
    '''
    # raw config (just scheme, always leads, player count) comparison
    testing_set = set()
    config_one = copy.deepcopy(game_config)
    testing_set.update([config_one])
    assert testing_set == {config_one}
    config_two = copy.deepcopy(game_config)
    testing_set.update([config_two])
    assert testing_set == {config_one}

    # masterminds
    testing_set = set()
    config_one = copy.deepcopy(game_config)
    config_one._masterminds.append(card_group_enum(1), "foobar")
    testing_set.update([config_one])
    assert testing_set == {config_one}
    config_two = copy.deepcopy(game_config)
    config_two._masterminds.append(card_group_enum(1), "foobar")
    testing_set.update([config_two])
    assert testing_set == {config_one}

    # loop through villain deck
    for card_class in VILLAIN_DECK:
        testing_set = set()
        config_one = copy.deepcopy(game_config)
        getattr(config_one.villain_deck, card_class).append(card_group_enum(1), "foobar")
        testing_set.update([config_one])
        assert testing_set == {config_one}
        config_two = copy.deepcopy(game_config)
        getattr(config_two.villain_deck, card_class).append(card_group_enum(1), "foobar")
        testing_set.update([config_two])
        assert testing_set == {config_one}

    # enforcers
    testing_set = set()
    config_one = copy.deepcopy(game_config)
    config_one._enforcers.append(card_group_enum(1), "foobar")
    testing_set.update([config_one])
    assert testing_set == {config_one}
    config_two = copy.deepcopy(game_config)
    config_two._enforcers.append(card_group_enum(1), "foobar")
    testing_set.update([config_two])
    assert testing_set == {config_one}

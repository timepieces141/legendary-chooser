'''
The components module holds all the definitions of the different components that
make up a game configuration, as well as the game configuration definition
itself.
'''

import logging

# legendary libraries
from . import rules
from . import util
from . exceptions import ConfigurationError, ValidationError

class ConfigurationComponent(object):
    '''
    A component of the game configuration - be it the set of masterminds,
    villains, or heroes. This holds the cards/card groups of the given game
    component, and the count of how many are needed to be complete.
    '''
    def __init__(self, card_class, card_class_use, count):
        '''
        Create an instance of a ConfigurationComponent.
        '''
        self.__card_class = card_class
        self.__card_class_use = card_class_use
        self.__count = count
        self._card_groups = {}

    @property
    def card_class(self):
        '''
        The card class of this configuration component. This translates to the
        set-specific type, such Masterminds, Villains, etc.
        '''
        return self.__card_class

    @property
    def card_class_use(self):
        '''
        The card class use of this configuration component. This translates to
        the use of the card, such as a Hero in the villain deck, as opposed to a
        hero in the hero deck.
        '''
        return self.__card_class_use

    @property
    def count(self):
        '''
        The number of card groups to add to this configuration to make it
        complete.
        '''
        return self.__count

    @property
    def card_groups(self):
        '''
        Retrieve the card groups loaded into this component.
        '''
        return self._card_groups

    def append(self, group, package):
        '''
        Add a card group and its package to the dictionary of card groups.
        '''
        self._card_groups[group] = package
        if len(self._card_groups) > self.__count:
            raise ConfigurationError("Too many '{}' added to this " \
                                     "configuration".format(self.__card_class_use.replace("_", " ")))

    def __str__(self):
        str_representation = "{}:".format(self.card_class)
        separator = ""
        for card_group, _ in self.card_groups.items():
            str_representation += "{} {}".format(separator, card_group.name)
            separator = ","
        return str_representation

    def __eq__(self, other):
        if isinstance(other, ConfigurationComponent):
            if (self.card_class != other.card_class or
                    self.card_class_use != other.card_class_use or
                    self.count != other.count):
                return False
            return self.card_groups.keys() == other.card_groups.keys()

        return NotImplemented

class VillainDeck(object):
    '''
    An encapsulation of the components that go in the villain deck
    '''
    def __init__(self, scheme, scheme_set_name, player_count):
        '''
        Create an instance of the Villain Deck
        '''
        scheme_package = util.get_package_from_name(scheme_set_name)

        # possible card groups in the villain deck
        self._villains = ConfigurationComponent("Villains", "villains",
                                                rules.count(scheme, scheme_package, player_count, "villains"))
        self._henchmen = ConfigurationComponent("Henchmen", "henchmen",
                                                rules.count(scheme, scheme_package, player_count, "henchmen"))
        self._heroes_in_villain_deck = ConfigurationComponent("Heroes", "heroes_in_villain_deck",
                                                              rules.count(scheme,
                                                                          scheme_package,
                                                                          player_count,
                                                                          "heroes_in_villain_deck"))

    @property
    def villains(self):
        '''
        The villains component of the villain deck.
        '''
        return self._villains

    @property
    def henchmen(self):
        '''
        The henchmen component of the villain deck.
        '''
        return self._henchmen

    @property
    def heroes_in_villain_deck(self):
        '''
        The heroes component of the villain deck.
        '''
        return self._heroes_in_villain_deck

    def __eq__(self, other):
        if isinstance(other, VillainDeck):
            for prop in ["villains", "henchmen", "heroes_in_villain_deck"]:
                if getattr(self, prop) != getattr(other, prop):
                    return False
            return True

        return NotImplemented

class GameConfiguration(object):
    '''
    A GameConfiguration instance is a concrete configuration of game components:
    a scheme, mastermind(s), villain(s), etc. It also provides a validation
    method that, as the configuration is built can rule it in or out as valid,
    based on rules from the rule book, text on the actual cards (schemes and
    masterminds), and house rules.
    '''
    def __init__(self, scheme, scheme_set_name, always_leads=True, player_count=1):
        '''
        Create an instance of a GameConfiguration. Initialize the data
        structures that will hold all of the configuration components.

        :param scheme:          the Scheme that bootstraps the game
                                configuration
        :param scheme_package:  the name of the package (legendary set) for the
                                scheme
        :param always_leads     Toggle on/off the "always leads" requirement for
                                villains on Masterminds
        :param player_count:    the number of players for this potential game
                                configuration, which is the first bit of meta
                                data on which validation happens.
        '''
        # pylint: disable=too-many-instance-attributes
        # I can't control how many components are in the game

        self.__scheme = (scheme, scheme_set_name)
        self.__always_leads = always_leads
        self.__player_count = player_count
        scheme_package = util.get_package_from_name(scheme_set_name)
        self._masterminds = ConfigurationComponent("Masterminds", "masterminds",
                                                   rules.count(scheme, scheme_package, player_count, "masterminds"))
        self._villain_deck = VillainDeck(scheme, scheme_set_name, player_count)
        self._enforcers = ConfigurationComponent("Villains", "enforcers",
                                                 rules.count(scheme, scheme_package, player_count, "enforcers"))
        self.heroes = {}

        # some logic
        self._next_component = ("Masterminds", "append_masterminds")

    @property
    def scheme(self):
        '''
        The configured Scheme object.
        '''
        return self.__scheme[0]

    @property
    def always_leads(self):
        '''
        The configured "always leads" setting.
        '''
        return self.__always_leads

    @property
    def player_count(self):
        '''
        The configured player count.
        '''
        return self.__player_count

    @property
    def masterminds(self):
        '''
        The configured masterminds component.
        '''
        return self._masterminds

    @property
    def villain_deck(self):
        '''
        The configured villain deck.
        '''
        return self._villain_deck

    @property
    def enforcers(self):
        '''
        The configured enforcers component.
        '''
        return self._enforcers

    def next_game_component(self):
        '''
        The method that determines what game component type needs to be added
        next. It follows the process of Masterminds -> Villains -> Henchmen ->
        Enforcers (if applicable) -> Heroes in the Villain Deck (if applicable),
        but checks the rules against the current configuration to know how many
        of each.
        '''
        # if we have masterminds (and really, how could we not?)
        if self._masterminds.count > 0:
            # and we don't have enough ...
            if len(self._masterminds.card_groups) < self._masterminds.count:
                return self._masterminds

        # if we have villains ...
        if self._villain_deck.villains.count > 0:
            # and we don't have enough ...
            if len(self._villain_deck.villains.card_groups) < self._villain_deck.villains.count:
                return self._villain_deck.villains

        # if we have henchmen ...
        if self._villain_deck.henchmen.count > 0:
            # and we don't have enough ...
            if len(self._villain_deck.henchmen.card_groups) < self._villain_deck.henchmen.count:
                return self._villain_deck.henchmen

        # if we have heroes in the villain deck ...
        if self._villain_deck.heroes_in_villain_deck.count > 0:
            # and we don't have enough ...
            component = self._villain_deck.heroes_in_villain_deck
            if len(component.card_groups) < component.count:
                return component

        # if we have villains in an enforcer deck...
        if self._enforcers.count > 0:
            # and we don't have enough ...
            if len(self._enforcers.card_groups) < self._enforcers.count:
                return self._enforcers

        # at this point, we're done
        return False

    def _check_required(self, component):
        '''
        Check if what's configured here is a superset of what is required in the
        rules.
        '''
        required = rules.required(self.__scheme[0],
                                  util.get_package_from_name(self.__scheme[1]),
                                  component.card_class_use)
        if required is not None:
            if not required.issubset(component.card_groups.keys()):
                return False

        return True

    def _check_exclusive(self, component):
        '''
        Check if what's configured here is a subset of what is required in the
        rules. Note, an empty set of component values here does *not* meet an
        exclusive requirement, if it exists.
        '''
        exclusive = rules.exclusive(self.__scheme[0],
                                    util.get_package_from_name(self.__scheme[1]),
                                    component.card_class_use)
        if exclusive is not None:
            if not set(component.card_groups.keys()).issubset(exclusive) or not component.card_groups.keys():
                return False

        return True

    def _simple_validate(self, component):
        '''
        Validate a card group.
        '''
        # raise and exception if the component under validation is not yet
        # complete (card_group length does not equal the necessary count)
        if len(component.card_groups) != component.count:
            raise ValidationError("The component '{}' was validated before it was " \
                                  "complete".format(component.card_class_use.replace("_", " ")))

        # required
        if not self._check_required(component):
            return False

        # exclusive
        if not self._check_exclusive(component):
            return False

        return True

    def _validate_villains(self):
        '''
        Validate villains - they are slightly different because of the "always
        leads" rule.
        '''
        # if always leads is True, make sure the villains set has the villain the mastermind always leads
        if self.__always_leads:
            # always leads villains for configured masterminds
            always_lead_villains = []
            for mastermind, mastermind_package_name in self._masterminds.card_groups.items():
                mastermind_package = util.get_package_from_name(mastermind_package_name)
                always_lead_villains.append(mastermind_package.Villains(mastermind.value))

            # if we have less villains than masterminds, all must be in
            # always leads, otherwise we only need as many successes as
            # there are masterminds
            successes_needed = min(len(self._villain_deck.villains.card_groups), len(self._masterminds.card_groups))
            for villain, _ in self._villain_deck.villains.card_groups.items():
                if villain in always_lead_villains:
                    successes_needed -= 1

            # check
            if successes_needed > 0:
                return False

        return self._simple_validate(self._villain_deck.villains)

    def _validate_scheme(self):
        '''
        Validate the scheme. This could easily be done by the *inverse* of the
        call to scheme_blacklisted at the moment, but this is a placeholder
        method for additional factors that may come into play (such as global
        house rules).
        '''
        # validate the scheme
        if rules.scheme_blacklisted(self.__scheme[0],
                                    util.get_package_from_name(self.__scheme[1]),
                                    self.__player_count):
            logging.debug("Config with blacklisted scheme \"%s\" marked as invalid", self.__scheme[0].name)
            return False

        return True

    def validate(self):
        '''
        Validate the game configuration so far. This method should only be
        called on component type "borders". Meaning, don't call this unless the
        component type as configured (*all* the masterminds, *all* the henchmen,
        etc.) is ready for validation.
        '''
        # if there are villains in an enforcer deck, validate them
        if self._enforcers.card_groups:

            return self._simple_validate(self._enforcers)

        # if there are heroes in the villain deck, validate them
        if self._villain_deck.heroes_in_villain_deck.card_groups:

            return self._simple_validate(self._villain_deck.heroes_in_villain_deck)

        # if there are henchmen, validate them
        if self._villain_deck.henchmen.card_groups:

            return self._simple_validate(self._villain_deck.henchmen)

        # # if there are villains, validate them
        if self._villain_deck.villains.card_groups:

            return self._validate_villains()

        # if there are masterminds, validate them
        if self._masterminds.card_groups:

            return self._simple_validate(self._masterminds)

        # and last, scheme
        return self._validate_scheme()


    def __str__(self):
        str_representation = "\nGame Configuration\n"
        str_representation += "\tScheme: {}\n".format(self.scheme.name)
        if self._masterminds.card_groups:
            str_representation += "\t{}\n".format(self._masterminds)
        if (self._villain_deck.villains.card_groups or
                self._villain_deck.henchmen.card_groups or
                self._villain_deck.heroes_in_villain_deck.card_groups):
            str_representation += "\tVillain Deck:\n"
        if self._villain_deck.villains.card_groups:
            str_representation += "\t\t{}\n".format(self._villain_deck.villains)
        if self._villain_deck.henchmen.card_groups:
            str_representation += "\t\t{}\n".format(self._villain_deck.henchmen)
        if self._villain_deck.heroes_in_villain_deck.card_groups:
            str_representation += "\t\t{}\n".format(self._villain_deck.heroes_in_villain_deck)
        if self._enforcers.card_groups:
            str_representation += "\tEnforcer Deck:\n"
            str_representation += "\t\t{}\n".format(self._enforcers)
        return str_representation

    def __repr__(self):
        representation = "<GameConfiguration Scheme=\"{}\"".format(self.scheme.name)
        for mastermind in sorted(self._masterminds.card_groups, key=lambda elem: elem.value):
            representation += " Mastermind=\"{}\"".format(mastermind.name)
        for villain in sorted(self._villain_deck.villains.card_groups, key=lambda elem: elem.value):
            representation += " Villain=\"{}\"".format(villain.name)
        for henchman in sorted(self._villain_deck.henchmen.card_groups, key=lambda elem: elem.value):
            representation += " Henchman=\"{}\"".format(henchman.name)
        for hero in sorted(self._villain_deck.heroes_in_villain_deck.card_groups, key=lambda elem: elem.value):
            representation += " Hero_in_Villain_Deck=\"{}\"".format(hero.name)
        for villain in sorted(self._enforcers.card_groups, key=lambda elem: elem.value):
            representation += " Enforcer=\"{}\"".format(villain.name)
        representation += ">"
        return representation

    def __eq__(self, other):
        if isinstance(other, GameConfiguration):
            props = [prop for prop in dir(GameConfiguration) if isinstance(getattr(GameConfiguration, prop), property)]
            for prop in props:
                if getattr(self, prop) != getattr(other, prop):
                    return False
            return True

        return NotImplemented

    def __hash__(self):
        hash_list = [self.scheme]
        hash_list = [self.always_leads]
        hash_list = [self.player_count]
        hash_list += sorted(self._masterminds.card_groups, key=lambda elem: elem.value)
        hash_list += sorted(self._villain_deck.villains.card_groups, key=lambda elem: elem.value)
        hash_list += sorted(self._villain_deck.henchmen.card_groups, key=lambda elem: elem.value)
        hash_list += sorted(self._villain_deck.heroes_in_villain_deck.card_groups, key=lambda elem: elem.value)
        hash_list += sorted(self._enforcers.card_groups, key=lambda elem: elem.value)
        return hash(tuple(hash_list))

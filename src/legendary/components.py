'''
The components module holds all the definitions of the different components that
make up a game configuration, as well as the game configuration definition
itself.
'''

import logging

# legendary libraries
from . import rules
from . import util

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
        self.scheme = (scheme, scheme_set_name)
        self.always_leads = always_leads
        self.player_count = player_count
        self.masterminds = {}
        self.villains = {}
        self.henchmen = {}
        self.enforcers = {}
        self.heroes_in_villain_deck = {}
        self.heroes = {}

        # some logic
        self._next_component = ("Masterminds", "append_masterminds")

        # retrieve counts for each part of the game config
        scheme_package = util.get_package_from_name(scheme_set_name)
        self.masterminds_count = rules.count(scheme, scheme_package, player_count, "masterminds")
        self.villains_count = rules.count(scheme, scheme_package, player_count, "villains")
        self.henchmen_count = rules.count(scheme, scheme_package, player_count, "henchmen")
        self.enforcers_count = rules.count(scheme, scheme_package, player_count, "enforcers")
        self.heroes_in_villain_deck_count = rules.count(scheme, scheme_package, player_count, "heroes_in_villain_deck")
        # self.heroes_count = rules.heroes_count(scheme, scheme_package, player_count)

    def append_masterminds(self, mastermind, mastermind_package):
        '''
        Add a Mastermind to the game configuration.
        '''
        self.masterminds[mastermind] = mastermind_package

    def append_villains(self, villain, villain_package):
        '''
        Add a Villain to the game configuration.
        '''
        self.villains[villain] = villain_package

    def append_henchmen(self, henchman, henchman_package):
        '''
        Add a Henchman to the game configuration.
        '''
        self.henchmen[henchman] = henchman_package

    def append_enforcers(self, enforcer, enforcer_package):
        '''
        Add a Villain for the Enforcer deck to the game configuration.
        '''
        self.enforcers[enforcer] = enforcer_package

    def append_heroes_in_villain_deck(self, hero, heroes_in_villain_deck_package):
        '''
        Add a Hero for the Villain deck to the game configuration.
        '''
        self.heroes_in_villain_deck[hero] = heroes_in_villain_deck_package

    def next_game_component(self):
        '''
        The method that determines what game component type needs to be added
        next. It follows the process of Masterminds -> Villains -> Henchmen ->
        Enforcers (if applicable) -> Heroes in the Villain Deck (if applicable),
        but checks the rules against the current configuration to know how many
        of each.
        '''
        # if we have masterminds (and really, how could we not?)
        if self.masterminds_count > 0:
            # and we don't have enough ..
            if len(self.masterminds) < self.masterminds_count:
                return ("Masterminds", "append_masterminds")

        # if we have villains ...
        if self.villains_count > 0:
            # and we don't have enough ...
            if len(self.villains) < self.villains_count:
                return ("Villains", "append_villains")

        # if we have henchmen ...
        if self.henchmen_count > 0:
            # and we don't have enough ...
            if len(self.henchmen) < self.henchmen_count:
                return ("Henchmen", "append_henchmen")

        # if we have villains in an enforcer deck...
        if self.enforcers_count > 0:
            # and we don't have enough ...
            if len(self.enforcers) < self.enforcers_count:
                return ("Villains", "append_enforcers")

        # if we have heroes in the villain deck ...
        if self.heroes_in_villain_deck_count > 0:
            # and we don't have enough ...
            if len(self.heroes_in_villain_deck) < self.heroes_in_villain_deck_count:
                return ("Heroes", "append_heroes_in_villain_deck")

        # at this point, we're done
        return False

    def _check_required(self, component_type, component_values):
        '''
        Check if what's configured here is a superset of what is required in the
        rules.
        '''
        required = rules.required(self.scheme[0], util.get_package_from_name(self.scheme[1]), component_type)
        if required is not None:
            if not required.issubset(component_values):
                return False

        return True

    def _check_exclusive(self, component_type, component_values):
        '''
        Check if what's configured here is a subset of what is required in the
        rules.
        '''
        exclusive = rules.exclusive(self.scheme[0], util.get_package_from_name(self.scheme[1]), component_type)
        if exclusive is not None:
            if not set(component_values).issubset(exclusive):
                return False

        return True

    def _simple_validate(self, card_group, card_group_dict):
        '''
        Validate a card group.
        '''
        # required
        if not self._check_required(card_group, card_group_dict.keys()):
            return False

        # exclusive
        if not self._check_exclusive(card_group, card_group_dict.keys()):
            return False

        return True

    def _validate_villains(self):
        '''
        Validate villains - they are slightly different because of the "always
        leads" rule.
        '''
        # if always leads is True, make sure the villains set has the villain the mastermind always leads
        if self.always_leads:
            # always leads villains for configured masterminds
            always_lead_villains = []
            for mastermind, mastermind_package_name in self.masterminds.items():
                mastermind_package = util.get_package_from_name(mastermind_package_name)
                always_lead_villains.append(mastermind_package.Villains(mastermind.value))

            # if we have less villains than masterminds, all must be in
            # always leads, otherwise we only need as many successes as
            # there are masterminds
            successes_needed = min(len(self.villains), len(self.masterminds))
            for villain, _ in self.villains.items():
                if villain in always_lead_villains:
                    successes_needed -= 1

            # check
            if successes_needed > 0:
                return False

        return self._simple_validate("villains", self.villains)

    def _validate_scheme(self):
        '''
        '''
        # validate the scheme
        if rules.scheme_blacklisted(self.scheme[0], util.get_package_from_name(self.scheme[1]), self.player_count):
            logging.debug("Config with blacklisted scheme \"%s\" marked as invalid", self.scheme[0].name)
            return False

        return True

    def validate(self):
        '''
        Validate the game configuration so far.
        '''
        # if there are heroes in the villain deck, validate them
        if self.heroes_in_villain_deck:

            return self._simple_validate("heroes_in_villain_deck", self.heroes_in_villain_deck)

        # if there are villains in the enforcer deck, validate them
        if self.enforcers:

            return self._simple_validate("enforcers", self.enforcers)

        # if there are henchmen, validate them
        if self.henchmen:

            return self._simple_validate("henchmen", self.henchmen)

        # # if there are villains, validate them
        if self.villains:

            return self._validate_villains()

        # if there are masterminds, validate them
        if self.masterminds:

            return self._simple_validate("masterminds", self.masterminds)

        # and last, scheme
        return self._validate_scheme()


    def __str__(self):
        string_repr = "\nGame Configuration\n"
        string_repr += "\tScheme: {}\n".format(self.scheme[0].name)
        for mastermind, _ in self.masterminds.items():
            string_repr += "\tMastermind: {}\n".format(mastermind.name)
        for villain, _ in self.villains.items():
            string_repr += "\tVillains: {}\n".format(villain.name)
        for henchman, _ in self.henchmen.items():
            string_repr += "\tHenchman: {}\n".format(henchman.name)
        return string_repr

    def __repr__(self):
        representation = "<GameConfiguration Scheme=\"{}\"".format(self.scheme[0])
        for mastermind in sorted(self.masterminds, key=lambda elem: elem.value):
            representation += " Mastermind=\"{}\"".format(mastermind)
        for villain in sorted(self.villains, key=lambda elem: elem.value):
            representation += " Villain=\"{}\"".format(villain)
        for henchman in sorted(self.henchmen, key=lambda elem: elem.value):
            representation += " Henchman=\"{}\"".format(henchman)
        representation += ">"
        return representation

    def __eq__(self, other):
        if isinstance(other, GameConfiguration):
            if (self.scheme[0] == other.scheme[0] and
                    self.masterminds.keys() == other.masterminds.keys() and
                    self.villains.keys() == other.villains.keys() and
                    self.henchmen.keys() == other.henchmen.keys()
               ):
                return True
        return NotImplemented

    def __hash__(self):
        hash_list = [self.scheme[0]]
        hash_list += sorted(self.masterminds, key=lambda elem: elem.value)
        hash_list += sorted(self.villains, key=lambda elem: elem.value)
        hash_list += sorted(self.henchmen, key=lambda elem: elem.value)
        return hash(tuple(hash_list))

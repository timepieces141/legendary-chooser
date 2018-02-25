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
        self.player_count = player_count
        self.always_leads = always_leads
        self.scheme = (scheme, scheme_set_name)
        self._next_component = ("Masterminds", "append_masterminds")
        self.masterminds = {}
        self.villains = {}
        self.henchmen = {}
        self.enforcers = {}
        self.heroes_in_villain_deck = {}
        self.heroes = {}

        # retrieve counts for each part of the game config
        scheme_package = util.get_package_from_name(scheme_set_name)
        self.masterminds_count = rules.masterminds_count(scheme, scheme_package, player_count)
        self.villains_count = rules.villains_count(scheme, scheme_package, player_count)
        self.henchmen_count = rules.henchmen_count(scheme, scheme_package, player_count)
        self.enforcers_count = rules.enforcers_count(scheme, scheme_package, player_count)
        self.heroes_in_villain_deck_count = rules.heroes_in_villain_deck_count(scheme, scheme_package, player_count)
        # self.heroes_count = rules.heroes_count(scheme, scheme_package, player_count)

    def append_masterminds(self, mastermind, mastermind_package):
        '''
        Add a Mastermind to the game configuration.
        '''
        self.masterminds[mastermind] = mastermind_package
        if len(self.masterminds) == self.masterminds_count:
            if self.villains_count > 0:
                self._next_component = ("Villains", "append_villains")
            elif self.henchmen_count > 0:
                self._next_component = ("Henchmen", "append_henchmen")
            elif self.enforcers_count > 0:
                self._next_component = ("Villains", "append_enforcers")
            elif self.heroes_in_villain_deck_count > 0:
                self._next_component = ("Heroes", "append_heroes_in_villain_deck")
            else:
                self._next_component = False

    def append_villains(self, villain, villain_package):
        '''
        Add a Villain to the game configuration.
        '''
        self.villains[villain] = villain_package
        if len(self.villains) == self.villains_count:
            if self.henchmen_count > 0:
                self._next_component = ("Henchmen", "append_henchmen")
            elif self.enforcers_count > 0:
                self._next_component = ("Villains", "append_enforcers")
            elif self.heroes_in_villain_deck_count > 0:
                self._next_component = ("Heroes", "append_heroes_in_villain_deck")
            else:
                self._next_component = False

    def append_henchmen(self, henchman, henchman_package):
        '''
        Add a Henchman to the game configuration.
        '''
        self.henchmen[henchman] = henchman_package
        if len(self.henchmen) == self.henchmen_count:
            if self.enforcers_count > 0:
                self._next_component = ("Villains", "append_enforcers")
            elif self.heroes_in_villain_deck_count > 0:
                self._next_component = ("Heroes", "append_heroes_in_villain_deck")
            else:
                self._next_component = False

    def append_enforcers(self, enforcer, enforcer_package):
        '''
        Add a Villain for the Enforcer deck to the game configuration.
        '''
        self.enforcers[enforcer] = enforcer_package
        if len(self.enforcers) == self.enforcers_count:
            if self.heroes_in_villain_deck_count > 0:
                self._next_component = ("Heroes", "append_heroes_in_villain_deck")
            else:
                self._next_component = False

    def append_heroes_in_villain_deck(self, hero, heroes_in_villain_deck_package):
        '''
        Add a Hero for the Villain deck to the game configuration.
        '''
        self.heroes_in_villain_deck[hero] = heroes_in_villain_deck_package
        if len(self.heroes_in_villain_deck) == self.heroes_in_villain_deck_count:
            self._next_component = False

    def validate(self):
        '''
        Validate the game configuration so far.
        '''
        # if there are heroes in the villain deck, validate them

        # if there are villains in the enforcer deck, validate them

        # if there are henchmen, validate them

        # if there are villains, validate them

        # # if there are masterminds, validate them
        if len(self.masterminds) > 0:

            # first up, required - which must be a subset of the masterminds here
            # configured
            required = rules.required_masterminds(self.scheme[0], util.get_package_from_name(self.scheme[1]))
            if required is not None:
                if not required.issubset(self.masterminds.keys()):
                    return False

            # next up, exclusive - the masterminds configured here must be a subset
            # the returned list
            exclusive = rules.exclusive_masterminds(self.scheme[0], util.get_package_from_name(self.scheme[1]))
            if exclusive is not None:
                if not self.masterminds.keys().issubset(exclusive):
                    return False

            # already validated the scheme
            return True

        # validate the scheme
        if rules.scheme_blacklisted(self.scheme[0], util.get_package_from_name(self.scheme[1]), self.player_count):
            return False

        return True

    def next_game_component(self):
        '''
        The next method knows what game component type needs to be added next.
        It follows the process of scheme -> mastermind -> villain -> henchman,
        but checks the rules against the current configuration to know how many
        of each.
        '''
        return self._next_component

    def __str__(self):
        '''
        String representation of this object.
        '''
        return "Game Configuration - Scheme: {}, Masterminds: {}, Villains: {}, " \
               "Henchmen: {}, Heroes in Villain Deck: {}, Heroes: {}".format(self.scheme[0].name,
                                                                             self.masterminds.keys(),
                                                                             self.villains.keys(),
                                                                             self.henchmen.keys(),
                                                                             self.heroes_in_villain_deck.keys(),
                                                                             self.heroes.keys()
                                                                            )

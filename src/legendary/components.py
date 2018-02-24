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
    def __init__(self, scheme, scheme_set_name, player_count=1):
        '''
        Create an instance of a GameConfiguration. Initialize the data
        structures that will hold all of the configuration components.

        :param scheme:          the Scheme that bootstraps the game
                                configuration
        :param scheme_package:  the name of the package (legendary set) for the
                                scheme
        :param player_count:    the number of players for this potential game
                                configuration, which is the first bit of meta
                                data on which validation happens.
        '''
        self.player_count = player_count
        self._next_component = None
        self.scheme = (scheme, scheme_set_name)
        self.masterminds = {}
        self.villains = {}
        self.henchmen = {}
        self.heroes_in_villain_deck = {}
        self.heroes = {}

    def append_masterminds(self, mastermind, mastermind_package):
        '''
        Add a mastermind to the game configuration.
        '''
        self.masterminds[mastermind] = mastermind_package

    def validate(self):
        '''
        Validate the game configuration so far.
        '''
        # validate the scheme against the rules
        if self.scheme[0] in rules.blacklisted_schemes(util.get_package_from_name(self.scheme[1]), self.player_count):
            return False

        # for now, if there's something in next component (it'll me "Masterminds"), then set it to False so we know we're done
        if self._next_component:
            self._next_component = False
        else:
            self._next_component = "Masterminds"
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

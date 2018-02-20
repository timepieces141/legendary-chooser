'''
The available module provides the functions for retrieving lists of "available"
types of cards in the Buffy the Vampire Slayer set, such as BigBads
(Masterminds), Schemes, Villains, Henchmen, and Heroes.
'''

from legendary.buffy.types import Schemes, Masterminds, Villains, Henchmen, Heroes

def available_schemes(player_count=1):
    '''
    Return a list of the available Schemes.

    TODO: Until I add configuration to the mix, this just returns a list with
    all of the Schemes.
    '''
    return list(Schemes)

def required_masterminds(schemes, player_count=1):
    '''
    Certain Schemes require certain Masterminds. Given the Scheme, and changed
    by any configuration effect (including house rules), return a list of the
    required Masterminds. Note that this can be, and often *will* be, an empty
    list.
    '''
    return []

def available_masterminds(player_count=1):
    '''
    Return a list of the available Masterminds.

    TODO: Until I add configuration to the mix, this just returns a list with
    all of the Masterminds.
    '''
    return list(Masterminds)

def required_villains(scheme, masterminds, player_count=1):
    '''
    Each Mastermind has a villain it "always leads." Some Schemes may require
    specific villains. For the given Scheme and the Masterminds, and changed by
    any configuration effect (including house rules), return a list of the
    required villains. Note that this can be an empty list.
    '''
    return []

def available_villains(player_count=1):
    '''
    Return a list of the available Villains.

    TODO: Until I add configuration to the mix, this just returns a list with
    all of the Villains.
    '''
    return list(Villains)

def required_henchmen(scheme, masterminds, player_count=1):
    '''
    Certain Schemes and Masterminds require certain Henchmen. For the given the
    Scheme and Masterminds, and changed by any configuration effect (including
    house rules), return a list of the required Henchmen. Note that this can be,
    and often *will* be, an empty list.
    '''
    return []

def available_henchmen(player_count=1):
    '''
    Return a list of the available Henchmen.

    TODO: Until I add configuration to the mix, this just returns a list with
    all of the Henchmen.
    '''
    return list(Henchmen)

def required_heroes_for_villain_deck(scheme, masterminds, player_count=1):
    '''
    Certain Schemes and Masterminds require certain Heroes in the *villain*
    deck. Given the Scheme and Mastermind, and changed by any configuration
    effect (including house rules), return a list of the required Heroes. Note
    that this can be, and often *will* be, an empty list.
    '''
    return []

def available_heroes_for_villain_deck(scheme, masterminds, player_count=1):
    '''
    Return a list of the available Heroes for the villain deck. This first has
    to check with the rules module to see if heroes are supposed to be in the
    villain deck for either the given scheme or mastermind, and if so, which
    ones. Then, possibly changed by any configuration effect (including house
    rules), returns the list of available heroes.
    '''
    return []

def required_heroes(scheme, masterminds, player_count=1):
    '''
    Certain Schemes and Masterminds require certain Heroes in the hero deck.
    Given the Scheme and Mastermind, and changed by any configuration effect
    (including house rules), return a list of the required Heroes. Note that
    this can be, and often *will* be, an empty list.
    '''
    return []

def available_heroes(player_count=1):
    '''
    Return a list of the available Heroes.

    TODO: Until I add configuration to the mix, this just returns a list with
    all of the Heroes.
    '''
    return list(Heroes)

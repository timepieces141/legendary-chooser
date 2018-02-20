'''
The rules module provides the specific setup rules for the Buffy the Vampire
Slayer set. There are functions for finding out, for instance, how many
villains, henchmen, and bystanders go into the Villain deck for a given player
count. This module also leverages the Buffy-specific user config that allows for
"house rules" to affect these counts and configurations.
'''

def mastermind_count(scheme, player_count=1):
    '''
    Return the number for masterminds for the given Scheme.

    TODO: Since we have not yet created a format for the rules configuration
    file where this would be stored, for now just return 1 (none of the Buffy
    schemes do this, so we're in the clear for now)
    '''
    return 1

def villain_count(scheme, masterminds, player_count=1):
    '''
    Return the number for villains for the given Scheme and Masterminds.

    TODO: Since we have not yet created a format for the rules configuration
    file where this would be stored, for now just return the number for the
    given player count.
    '''
    if player_count == 1:
        return 1
    elif player_count == 2:
        return 2
    elif player_count == 3 or player_count == 4:
        return 3
    else:
        return 4

def henchmen_count(scheme, masterminds, player_count=1):
    '''
    Return the number for henchmen for the given Scheme and Masterminds.

    TODO: Since we have not yet created a format for the rules configuration
    file where this would be stored, for now just return the number for the
    given player count.
    '''
    if player_count < 4:
        return 1
    else:
        return 2

def heroes_for_villain_deck_count(scheme, masterminds, player_count=1):
    '''
    Return the number for heroes to put in the villain deck for the given Scheme
    and Masterminds.

    TODO: Since we have not yet created a format for the rules configuration
    file where this would be stored, for now just return 0.
    '''
    return 0

def hero_count(scheme, masterminds, player_count=1):
    '''
    Return the number for heroes for the given Scheme and Masterminds.

    TODO: Since we have not yet created a format for the rules configuration
    file where this would be stored, for now just return the number for the
    given player count.
    '''
    if player_count == 1:
        return 3
    elif player_count < 5:
        return 5
    else:
        return 6

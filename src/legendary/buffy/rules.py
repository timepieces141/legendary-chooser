'''
The rules module holds the default rules configuration(s) for the Buffy the
Vampire Slayer set.
'''

def get_base_rules_config():
    '''
    Retrieve the base rules configuration.
    '''
    global _BASE_RULES_CONFIG
    return _BASE_RULES_CONFIG

def set_base_rules_config(config):
    '''
    Set the base rules configuration.
    '''
    global _BASE_RULES_CONFIG
    _BASE_RULES_CONFIG = config

# the loaded base rules configuration
_BASE_RULES_CONFIG = None

# base rules configuration to be saved upon first start up
DEFAULT_BASE_RULES_CONFIG = '''
{
    "player_counts": {
        "1": {
            "masterminds": 1,
            "villains": 1,
            "henchmen": 1,
            "heroes_in_villain_deck": 0,
            "enforcers": 0,
            "heroes": 3
        },
        "2": {
            "masterminds": 1,
            "villains": 2,
            "henchmen": 1,
            "heroes_in_villain_deck": 0,
            "enforcers": 0,
            "heroes": 5
        },
        "3": {
            "masterminds": 1,
            "villains": 3,
            "henchmen": 1,
            "heroes_in_villain_deck": 0,
            "enforcers": 0,
            "heroes": 5
        },
        "4": {
            "masterminds": 1,
            "villains": 3,
            "henchmen": 2,
            "heroes_in_villain_deck": 0,
            "enforcers": 0,
            "heroes": 5
        },
        "5": {
            "masterminds": 1,
            "villains": 4,
            "henchmen": 2,
            "heroes_in_villain_deck": 0,
            "enforcers": 0,
            "heroes": 6
        }
    },
    "blacklisted_schemes": {
        "1": [4]
    },
    "scheme_rules": {
        "2": {
            "heroes_in_villain_deck": {
                "diff": 1
            }
        },
        "3": {
            "henchmen": {
                "required": [1]
            }
        },
        "6": {
            "villains": {
                "diff": -1
            },
            "heroes_in_villain_deck": {
                "diff": 1,
                "exclusive": [3, 5, 7, 12]
            }
        }
    }
}
'''

def get_house_rules_config():
    '''
    Retrieve the house rules configuration.
    '''
    global _HOUSE_RULES_CONFIG
    return _HOUSE_RULES_CONFIG

def set_house_rules_config(config):
    '''
    Set the house rules configuration.
    '''
    global _HOUSE_RULES_CONFIG
    _HOUSE_RULES_CONFIG = config

# the loaded house rules configuration
_HOUSE_RULES_CONFIG = None

# house rules configuration to be save upon first start up
DEFAULT_HOUSE_RULES_CONFIG = '''
{

}
'''

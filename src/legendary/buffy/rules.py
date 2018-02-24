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
    "scheme": {
        "player_count": {
            "1": {
                "blacklisted": [4]
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

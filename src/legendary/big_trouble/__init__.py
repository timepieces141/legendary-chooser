'''
The Package that holds all the configuration and theme-specific logic for the
Big Trouble in Little China Legendary set.
'''

from . rules import (DEFAULT_BASE_RULES_CONFIG,
                     DEFAULT_HOUSE_RULES_CONFIG,
                     get_base_rules_config,
                     set_base_rules_config,
                     get_house_rules_config,
                     set_house_rules_config,
                    )
from . types import (Masterminds,
                     Schemes,
                     Villains,
                     Henchmen,
                     Heroes
                    )

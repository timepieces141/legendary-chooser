'''
The types module provides the enums of all the different types of cards in the
Big Trouble in Little China set, such as Masterminds, Schemes, Villains,
Henchmen, and Heroes.
'''

from enum import Enum
import itertools

# masterminds
_BIG_TROUBLE_MASTERMINDS = {
    1: ["Six Shooter", "SIX_SHOOTER"],
    2: ["Ching Dai", "CHING_DAI"],
    3: ["David Lo Pan", "DAVID_LO_PAN"],
    4: ["Sorcerous Lo Pan", "SORCEROUS_LO_PAN"],
}

Masterminds = Enum(  # pylint: disable=invalid-name
    value="Masterminds",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BIG_TROUBLE_MASTERMINDS.items()
    )
)

# schemes
_BIG_TROUBLE_SCHEMES = {
    1: ["Forge Crime Syndicate", "FORGE_CRIME SYNDICATE"],
    2: ["Rampage for Sacrifices", "RAMPAGE_FOR_SACRIFICES"],
    3: ["Flood Chinatown in Mediocrity", "FLOOD_CHINATOWN_IN_MEDIOCRITY"],
    4: ["Kill Uncle Chu", "KILL_UNCLE_CHU"],
    5: ["Corrupt True Heroes", "CORRUPT_TRUE_HEROES"],
    6: ["Assassination", "ASSASSINATION"],
    7: ["Destroy Chinatown's Dreams", "DESTROY_CHINATOWNS_DREAMS"],
    8: ["Fill the Hell of Upside Down Sinners", "FILL_THE_HELL_OF_UPSIDE_DOWN_SINNERS"],
    9: ["Enforce Villainous Hierarchy", "ENFORCE_VILLAINOUS_HIERARCHY"],
    10: ["Ruin San Fran", "RUIN_SAN_FRAN"],
    11: ["Open the Hell Gates", "OPEN_THE_HELL_GATES"],
    12: ["One and the Same Person, Jack", "ONE_AND_THE_SAME_PERSON_JACK"],
}

Schemes = Enum(  # pylint: disable=invalid-name
    value="Schemes",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BIG_TROUBLE_SCHEMES.items()
    )
)

# villains
_BIG_TROUBLE_VILLAINS = {
    1: ["Wing Kong Gang", "WING_KONG_GANG"],
    2: ["Monsters", "MONSTESR"],
    3: ["Wing Kong Exchange", "WING_KONG_EXCHANGE"],
    4: ["Warriors of Lo Pan", "WARRIORS_OF_LO_PAN"],
}

Villains = Enum(  # pylint: disable=invalid-name
    value="Villains",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BIG_TROUBLE_VILLAINS.items()
    )
)

# henchmen
_BIG_TROUBLE_HENCHMEN = {
    1: ["Lords of Death", "LORDS_OF_DEATH"],
    2: ["Ceremonial Warriors", "CEREMONIAL_WARRIORS"],
    3: ["Wing Kong Thugs", "WING_KONG_THUGS"],
}

Henchmen = Enum(  # pylint: disable=invalid-name
    value="Henchmen",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BIG_TROUBLE_HENCHMEN.items()
    )
)

# heroes
_BIG_TROUBLE_HEROES = {
    1: ["Jack Burton", "JACK_BURTON"],
    2: ["Wang Chi", "WANG_CHI"],
    3: ["Egg Shen", "EGG_SHE"],
    4: ["Gracie Law", "GRACIE_LAW"],
    5: ["Miao Yin", "MIAO_YIN"],
    6: ["Eddie", "EDDIE"],
    7: ["Margo", "MARGO"],
    8: ["Pork Chop Express", "PORK_CHOP_EXPRESS"],
    9: ["Henry Swanson", "HENRY_SWANSON"],
}

Heroes = Enum(  # pylint: disable=invalid-name
    value="Heroes",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BIG_TROUBLE_HEROES.items()
    )
)

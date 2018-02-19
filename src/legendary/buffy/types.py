'''
The types module provides the enums of all the different types of cards in the
Buffy the Vampire Slayer set, such as BigBads (Masterminds), Schemes, Villains,
Henchmen, and Heroes.
'''

from enum import Enum
import itertools

# masterminds
_BUFFY_MASTERMINDS = {
    1: ["The Master", "THE_MASTER"],
    2: ["Glorificus", "GLORIFICUS"],
    3: ["The Mayor", "THE_MAYOR"],
    4: ["Angelus", "ANGELUS"],
    5: ["The First", "THE_FIRST"],
}

Masterminds = Enum(  # pylint: disable=invalid-name
    value="Masterminds",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BUFFY_MASTERMINDS.items()
    )
)

# schemes
_BUFFY_SCHEMES = {
    1: ["Hellmouth Opening", "HELLMOUTH_OPENING"],
    2: ["Convert to Evil", "CONVERT_TO_EVIL"],
    3: ["Summon the Uber Vamps", "SUMMON_THE_UBER_VAMPS"],
    4: ["Twilight Terror", "TWILIGHT_TERROR"],
    5: ["Vile Agenda", "VILE_AGENDA"],
    6: ["Road to Damnation", "ROAD_TO_DAMNATION"],
    7: ["Epic Struggle", "EPIC_STRUGGLE"],
    8: ["Darkness Falls", "DARKNESS_FALLS"],
}

Schemes = Enum(  # pylint: disable=invalid-name
    value="Schemes",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BUFFY_SCHEMES.items()
    )
)

# villains
_BUFFY_VILLAINS = {
    1: ["Order of Aurelius", "ORDER_OF_AURELIUS"],
    2: ["Glory's Minions", "GLORYS_MINIONS"],
    3: ["The Mayor's Minions", "THE_MAYORS_MINIONS"],
    4: ["Scourge of Europe", "SCOURGE_OF_EUROPE"],
    5: ["The First's Minions", "THE_FIRSTS_MINIONS"],
    6: ["Demons", "DEMONS"],
    7: ["Harmony's Gang", "HARMONYS_GANG"],
}

Villains = Enum(  # pylint: disable=invalid-name
    value="Villains",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BUFFY_VILLAINS.items()
    )
)

# henchmen
_BUFFY_HENCHMEN = {
    1: ["Turok-han Vampires", "TUROK_HAN_VAMPIRES"],
    2: ["Vampire Initiate", "VAMPIRE_INITIATE"],
    3: ["Shark Gangsters", "SHARK_GANGSTERS"],
    4: ["Harbingers Of Death", "HARBINGERS_OF_DEATH"],
    5: ["Hellhounds", "HELLHOUNDS"],
}

Henchmen = Enum(  # pylint: disable=invalid-name
    value="Henchmen",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BUFFY_HENCHMEN.items()
    )
)

# heroes
_BUFFY_HEROES = {
    1: ["Buffy Summers", "BUFFY_SUMMERS"],
    2: ["Xander Harris", "XANDER_HARRIS"],
    3: ["Willow Rosenberg", "WILLOW_ROSENBERG"],
    4: ["Rupert Giles", "RUPERT_GILES"],
    5: ["Spike", "SPIKE"],
    6: ["Anya Jenkins", "ANYA_JENKINS"],
    7: ["Angel", "ANGEL"],
    8: ["Cordelia Chase", "CORDELIA_CHASE"],
    9: ["Tara Maclay", "TARA_MACLAY"],
    10: ["Daniel 'Oz' Osbourne", "DANIEL_OZ_OSBOURNE"],
    11: ["Riley Finn", "RILEY_FINN"],
    12: ["Faith", "FAITH"],
    13: ["Jenny Calendar", "JENNY_CALENDAR"],
    14: ["Buffybot", "BUFFYBOT"],
    15: ["The First Slayer", "THE_FIRST_SLAYER"],
}

Heroes = Enum(  # pylint: disable=invalid-name
    value="Heroes",
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _BUFFY_HEROES.items()
    )
)

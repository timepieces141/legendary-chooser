#!/usr/bin/env python3

'''
This script is the entry point for the Legendary Chooser command line tool.

Additional packages are necessary to use this script. These can be found in the
requirements.txt file beside this script. If you do not wish to have these
packages installed globally, the use of a virtual environment is encouraged.
Either way, to install, use the command:

    pip install -r requirements.txt

Keep in mind this script uses python 3, so your virtual environment should be
launched accordingly:

    mkvirtualenv -p `which python3.6` legendary

Happy gaming.
'''

# core libraries
import errno
import importlib
import logging
import os
import random

# third party libraries
from appdirs import user_data_dir
import click

# logger configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

LEGENDARY_SETS = [
    "buffy",
    "big_trouble"
]

def get_version():
    '''
    Retrieves the version of this package
    '''
    import pkg_resources
    return pkg_resources.require("legendary-chooser")[0].version


@click.group()
@click.version_option(version=get_version(), message="Legendary Chooser\nversion %(version)s")
@click.pass_context
def cli(ctx):
    '''
    Command Line Utility for choosing Legendary configurations, saving game
    plays of specific configurations, and launching analysis tools.
    '''
    # initialize the context object as a dictionary
    ctx.obj = {}

    # ensure the data directory exists
    data_dir = user_data_dir("legendary", "Edward Petersen")
    ctx.obj["data_dir"] = data_dir
    try:
        os.makedirs(data_dir)
        logging.debug("Creating the user data directory at: {}", data_dir)
    except OSError as os_error:
        if os_error.errno != errno.EEXIST:
            raise

def validate_sets(ctx, param, value):
    '''
    Validate the paramater passed as a possible Legendary set.
    '''
    if value.lower() in LEGENDARY_SETS:
        return value.lower()
    else:
        raise click.BadParameter("'{}' is not an available Legendary set for configuration".format(value))

@cli.command()
@click.option('-s', '--include-set', required=True, callback=validate_sets)
@click.option('-c', '--player-count', default=1)
@click.pass_context
def generate(ctx, include_set, player_count):
    '''
    Generate a game configuration, complete with Mastermind, Scheme, Villain
    Deck Configuration, and Hero Deck Configuration.
    '''
    # dynamically load the "set" package to access the Schemes, Masterminds,
    # etc.
    spec = importlib.util.find_spec("legendary.{}".format(include_set))
    set_package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(set_package)

    # choose a random scheme
    available_schemes = set_package.available_schemes(player_count)
    scheme = random.SystemRandom().choice(available_schemes)

    # retrieve the required masterminds, if any
    required_masterminds = set_package.required_masterminds(scheme, player_count)

    # if there are required masterminds, our work is done, otherwise retireve
    # the available masterminds and choose as many as required
    if len(required_masterminds) > 0:
        masterminds = required_masterminds
    else:
        mastermind_count = set_package.mastermind_count(scheme, player_count)
        available_masterminds = set_package.available_masterminds(player_count)
        masterminds = []

        # loop until we have all the configured number of masterminds
        while len(masterminds) < mastermind_count:
            selected_mastermind = random.SystemRandom().choice(available_masterminds)
            available_masterminds.remove(selected_mastermind)
            masterminds.append(selected_mastermind)

    # grab the required villains
    villains = set()
    villains.update(set_package.required_villains(scheme, masterminds, player_count))

    # find out how many villains are required for the villain deck
    villain_count = set_package.villain_count(scheme, masterminds, player_count)

    # some game configurations *remove* villains from the villain deck - if the
    # villains list is already too big, truncate it
    villains = list(villains)
    del villains[villain_count:]
    villains = set(villains)

    # retrieve the available villains
    available_villains = set_package.available_villains(player_count)

    # loop until we have all the configured number of villains
    while len(villains) < villain_count:
        selected_villain = random.SystemRandom().choice(available_villains)
        available_villains.remove(selected_villain)
        villains.update([selected_villain])

    # grab the required henchmen
    henchmen = set()
    henchmen.update(set_package.required_henchmen(scheme, masterminds, player_count))

    # find out how many henchmen are required for the villain deck
    henchmen_count = set_package.henchmen_count(scheme, masterminds, player_count)

    # some game configurations *remove* henchmen from the villain deck - if the
    # henchmen list is already too big, truncate it
    henchmen = list(henchmen)
    del henchmen[henchmen_count:]
    henchmen = set(henchmen)

    # retrieve the available henchmen
    available_henchmen = set_package.available_henchmen(player_count)

    # loop until we have all the configured number of henchmen
    while len(henchmen) < henchmen_count:
        selected_henchman = random.SystemRandom().choice(available_henchmen)
        available_henchmen.remove(selected_henchman)
        henchmen.update([selected_henchman])

    # grab the required heroes for the villain deck
    heroes_for_villain_deck = set()
    heroes_for_villain_deck.update(set_package.required_heroes_for_villain_deck(scheme, masterminds, player_count))

    # find out how many heroes are required for the villain deck
    heroes_for_villain_deck_count = set_package.heroes_for_villain_deck_count(scheme, masterminds, player_count)

    # retrieve the available heroes (that can be put in the villain deck)
    available_heroes_for_villain_deck = set_package.available_heroes_for_villain_deck(scheme, masterminds, player_count)

    # loop until we have all the configured number of heroes for the villain
    # deck
    while len(heroes_for_villain_deck) < heroes_for_villain_deck_count:
        selected_hero = random.SystemRandom().choice(available_heroes_for_villain_deck)
        available_heroes_for_villain_deck.remove(selected_hero)
        heroes_for_villain_deck.update([selected_hero])

    # grab the required heroes
    heroes = set()
    heroes.update(set_package.required_heroes(scheme, masterminds, player_count))

    # find out how many heroes are required for the hero deck
    hero_count = set_package.hero_count(scheme, masterminds, player_count)

    # retrieve the available heroes
    available_heroes = set_package.available_heroes(player_count)

    # loop until we have all the configured number of heroes
    while len(heroes) < hero_count:
        selected_hero = random.SystemRandom().choice(available_heroes)
        available_heroes.remove(selected_hero)
        heroes.update([selected_hero])

    logging.info("Scheme: %s, Mastermind(s): %s, Villain(s): %s, Henchmen: %s, Heroes: %s",
                 scheme.name,
                 ', '.join([mastermind.name for mastermind in masterminds]),
                 ', '.join([villain.name for villain in villains]),
                 ', '.join([henchman.name for henchman in henchmen]),
                 ', '.join([hero.name for hero in heroes])
                )

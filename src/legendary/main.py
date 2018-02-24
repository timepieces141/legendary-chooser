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
import copy
import logging

# third party libraries
import click

# legendary libraries
# from . import rules
from . components import GameConfiguration
from . import util

# available sets
LEGENDARY_SETS = [
    "buffy",
    "big_trouble"
]

# for verbosity
LOGGING_LEVELS = {
    "0": logging.CRITICAL,
    "1": logging.ERROR,
    "2": logging.WARNING,
    "3": logging.INFO,
    "4": logging.DEBUG,
}

def get_version():
    '''
    Retrieves the version of this package
    '''
    import pkg_resources
    return pkg_resources.require("legendary-chooser")[0].version


@click.group()
@click.version_option(version=get_version(), message="Legendary Chooser\nversion %(version)s")
@click.option('-v', '--verbosity', count=True, help="Set the level of verbosity. Multiple options increase the verbosity")
@click.pass_context
def cli(ctx, verbosity):
    '''
    Command Line Utility for choosing Legendary configurations, saving game
    plays of specific configurations, and launching analysis tools.
    '''
    # set the logging based on the verbosity
    if verbosity > 4:
        verbosity = 4
    logging.basicConfig(level=LOGGING_LEVELS[str(verbosity)], format='%(asctime)s - %(levelname)s: %(message)s')

    # initialize the context object as a dictionary
    ctx.obj = {}

def validate_sets(ctx, param, value):
    '''
    Validate the paramater passed as a possible Legendary set.
    '''
    # there can be multiple legendary sets, so loop through and check each one
    for possible in value:
        if possible.lower() not in LEGENDARY_SETS:
            logging.error("Legendary sets provided: %s", value)
            error_msg = "'{}' is not an available Legendary set for configuration".format(possible)
            logging.error(error_msg)
            raise click.BadParameter(error_msg)

    return value

@cli.command()
@click.option('-s', '--include-set', required=True, multiple=True, callback=validate_sets)
@click.option('-c', '--player-count', default=1)
@click.pass_context
def generate(ctx, include_set, player_count):
    '''
    Generate a game configuration, complete with Mastermind, Scheme, Villain
    Deck Configuration, and Hero Deck Configuration.
    '''
    # loop through the included sets and load the necessary packages
    imported_packages = []
    for legendary_set in include_set:
        imported_packages.append(util.get_package_from_name("legendary.{}".format(legendary_set)))

    # data structures for holding game configs
    final_game_configs = []
    to_process = []

    # bootstrap with scheme-filled game configs
    for legendary_set in imported_packages:
        for scheme in legendary_set.Schemes:
            game_config = GameConfiguration(scheme, legendary_set.__name__, player_count)
            if game_config.validate():
                to_process.append(game_config)

    # loop until processing list is empty
    while len(to_process) > 0:
        # grab a game config
        game_config = to_process.pop()

        # find out what card class is next (Masterminds, Villains, or Henchmen)
        next_card_class = game_config.next_game_component()

        # loop through the included sets
        for legendary_set in imported_packages:

            # loop through all the values of the next card group in the
            # legendary set
            card_class = getattr(legendary_set, next_card_class)
            for card_group in card_class:

                # clone the game config
                new_config = copy.deepcopy(game_config)

                # add the new card group
                getattr(new_config, "append_{}".format(card_class.__name__.lower()))(card_group, legendary_set.__name__)

                # validate
                if new_config.validate():

                    # if there's more to add to the config, append it for
                    # processing
                    if new_config.next_game_component():
                        to_process.append(new_config)

                    # we're done, add it to the final list
                    else:
                        final_game_configs.append(new_config)

    # we now have all the valid game configs (minus heroes) - time to choose one, so dish off to the configured decision engine
    # for game_config in final_game_configs:
    #     logging.info(game_config)

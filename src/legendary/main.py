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


# @click.option('-m', '--mvee-dir', required=True, type=click.Path(exists=True, readable=True, resolve_path=True),
#               help="The path to the MVEE installation directory, complete with bin/monitor, bin/mvee.ko, " \
#                    "lib/libsync_sandwich.so, etc.")

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
@click.pass_context
def generate(ctx, include_set):
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
    scheme = random.SystemRandom().choice(list(set_package.Schemes))

    # choose a random mastermind
    mastermind = random.SystemRandom().choice(list(set_package.Masterminds))

    # choose the "always leads" villain
    villain = set_package.Villains(mastermind.value)

    # choose a random henchman
    henchman = random.SystemRandom().choice(list(set_package.Henchmen))

    # choose three heroes
    available_heroes = list(set_package.Heroes)
    selected_heroes = []
    for i in range(3):
        hero = random.SystemRandom().choice(list(available_heroes))
        available_heroes.remove(hero)
        selected_heroes.append(hero)

    logging.info("Scheme: %s, Mastermind: %s, Villain: %s, Henchman: %s, Heroes: %s",
                 scheme.name,
                 mastermind.name,
                 villain.name,
                 henchman.name,
                 ', '.join([hero.name for hero in selected_heroes])
                )

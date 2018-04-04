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
import logging
from textwrap import fill

# third-party libraries
import click

# legendary libraries
from . exceptions import LegendaryError
from . import util
# from . util import PACKAGED_LEGENDARY_SETS, LOGGING_LEVELS, restore_file, initialize, available_sets

class MutuallyExclusiveOption(click.Option):
    '''
    A custom Click option for handling mutually exclusive arguments given on the
    command line.
    '''
    def __init__(self, *args, **kwargs):
        '''
        During construction grab out our new mutually_exclusive parameter and
        store it.
        '''
        # kwargs should have an entry for the listing the option(s) this option
        # is mutually exclusive with.
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        '''
        Check for the mutually exclusive options
        '''
        # if both this option's value and the option(s) from mutually
        # exclusive's value evaluate to True (meaning they have argument
        # value(s) or are positive flags), raise an error
        if self.name in opts and opts[self.name]:
            for other in self.mutually_exclusive:
                if other in opts and opts[other]:
                    raise click.UsageError("Options '{}' and '{}' are mutually exclusive".format(self.name, other))

        return super().handle_parse_result(ctx, opts, args)

def get_version():
    '''
    Retrieves the version of this package
    '''
    import pkg_resources
    return pkg_resources.get_distribution("legendary-chooser").version


def validate_sets(ctx, param, value): # pylint: disable=unused-argument
    '''
    Validate the paramater passed as a possible Legendary set.
    '''
    # retrieve the loaded sets
    available = util.available_sets()

    # since we want to know what individual sets provided are not supported,
    # loop through them
    error_msgs = ""
    for possible in value:
        if possible.lower() not in available:
            error_msg = "'{}' is not an available Legendary set. ".format(possible.lower())
            error_msgs += error_msg
            logging.error(error_msg)

    # raise the error
    if error_msgs:
        avail_list = " and ".join([", ".join(available[:-1]), available[-1]] if len(available) > 2 else available)
        raise click.BadParameter(error_msgs + "The available Legendary sets are: {}".format(avail_list))

    # or return the value
    return value


@click.group()
@click.version_option(version=get_version(), message="Legendary Chooser\nversion %(version)s")
@click.option('-v', '--verbosity', count=True,
              help="Set the level of verbosity. Multiple options increase the verbosity")
def cli(verbosity):
    '''
    Command Line Utility for choosing Legendary configurations, saving game
    plays of specific configurations, and launching analysis tools.
    '''
    # set the logging based on the verbosity
    if verbosity > 4:
        verbosity = 4
    logging.basicConfig(level=util.LOGGING_LEVELS[str(verbosity)], format='%(asctime)s - %(levelname)s: %(message)s')

    # initialize, if necessary
    util.initialize()

@cli.command()
@click.option('-s', '--set', 'legendary_sets',
              help='Restore the default configuration for a given Legenday set [mutually exclusive with --all]',
              multiple=True, type=click.Choice(util.PACKAGED_LEGENDARY_SETS),
              cls=MutuallyExclusiveOption, mutually_exclusive=["all_sets"])
@click.option('-a', '--all', 'all_sets', is_flag=True,
              help='Restore the default configuration(s) for *all* Legenday set(s) [mutually exclusive with --set]',
              cls=MutuallyExclusiveOption, mutually_exclusive=["legendary_sets"])
def restore(legendary_sets, all_sets):
    '''
    Restore the default configuration file(s) for the given Legendary set(s).
    '''
    if all_sets:
        util.initialize(False)
    elif legendary_sets:
        # loop through sets
        for legendary_set in legendary_sets:
            try:
                util.restore_file(legendary_set)
            except LegendaryError as legendary_error:
                click.echo(fill(str(legendary_error)))
                raise click.Abort()
    else:
        try:
            util.restore_file("")
        except LegendaryError as legendary_error:
            click.echo(fill(str(legendary_error)))
            raise click.Abort()

@cli.command()
@click.option('-s', '--include-set', 'included_sets', required=True, multiple=True, callback=validate_sets)
@click.option('-c', '--player-count', default=1)
@click.option('--always-leads/--disable-always-leads', default=True)
def generate(included_sets, player_count, always_leads):
    '''
    Generate a game configuration, complete with Mastermind, Scheme, Villain
    Deck Configuration, and Hero Deck Configuration.
    '''
    pass

# @cli.command()
# @click.option('-s', '--include-set', required=True, multiple=True, callback=validate_sets)
# @click.option('-c', '--player-count', default=1)
# @click.option('--always-leads/--disable-always-leads', default=True)
# def generate(include_set, player_count, always_leads):
#     '''
#     Generate a game configuration, complete with Mastermind, Scheme, Villain
#     Deck Configuration, and Hero Deck Configuration.
#     '''
#     # loop through the included sets and load the necessary packages and rules
#     # configs
#     imported_packages = []
#     for legendary_set in include_set:
#         set_package = util.get_package_from_name("legendary.{}".format(legendary_set))
#         imported_packages.append(set_package)
#         for rule_set in ["base", "house"]:
#             load_rules_configuration(set_package, rule_set)

#     # data structures for holding game configs
#     final_game_configs = set()
#     to_process = []

#     # bootstrap with scheme-filled game configs
#     for legendary_set in imported_packages:
#         for scheme in legendary_set.Schemes:
#             game_config = GameConfiguration(scheme, legendary_set.__name__, always_leads, player_count)
#             if game_config.validate():
#                 to_process.append(game_config)

#     # loop until processing list is empty
#     while len(to_process) > 0:

#         # grab a game config
#         game_config = to_process.pop()

#         # find out what card class is next (Masterminds, Villains, or Henchmen)
#         next_card_class, append_method = game_config.next_game_component()

#         # loop through the included sets
#         for legendary_set in imported_packages:

#             # loop through all the values of the next card group in the
#             # legendary set
#             card_class = getattr(legendary_set, next_card_class)
#             for card_group in card_class:

#                 # clone the game config
#                 new_config = copy.deepcopy(game_config)

#                 # add the new card group
#                 dup_detector = len(getattr(new_config, next_card_class.lower()))
#                 getattr(new_config, append_method)(card_group, legendary_set.__name__)

#                 # if this addition didn't change the config, we just tried to
#                 # add a card class the config already had - toss this one
#                 if dup_detector == len(getattr(new_config, next_card_class.lower())):
#                     continue

#                 # only validate at game component borders - if
#                 # next_game_component returns something (not False), check if we
#                 # are set to add the same component we just did
#                 if new_config.next_game_component():
#                     if next_card_class == new_config.next_game_component()[0]:
#                         to_process.append(new_config)
#                         continue

#                 # if we're on a component border, validate
#                 if new_config.validate():

#                     # if there are more components to add, append it for further
#                     # processing
#                     if new_config.next_game_component():
#                         to_process.append(new_config)

#                     # we're done, add it to the final list
#                     else:
#                         final_game_configs.update([new_config])

    # # we now have all the valid game configs (minus heroes) - time to choose
    # # one, so dish off to the configured decision engine
    # for game_config in final_game_configs:
    #     logging.info(game_config.__repr__())

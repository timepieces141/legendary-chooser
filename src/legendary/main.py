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

# third party libraries
import click

def get_version():
    '''
    Retrieves the version of this package
    '''
    import pkg_resources
    return pkg_resources.require("legendary-chooser")[0].version


@click.group()
@click.version_option(version=get_version(), message="Legendary Chooser\nversion %(version)s")
def cli():
    '''
    Command Line Utility for choosing Legendary configurations, saving previous
    configurations, and launching analysis tools.
    '''
    pass

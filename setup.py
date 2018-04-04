'''
Build and distribute the Legendary Chooser!
'''

# core libraries
from codecs import open # pylint: disable=redefined-builtin
import importlib.util
import logging
import os
import re
import subprocess
import sys

# third party libraries
from setuptools import setup

# logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
SETUP_LOGGER = logging.getLogger('legendary-chooser')

# classifications for this project - see
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    # project is in the alpha stage
    'Development Status :: 3 - Alpha',

    # MIT license
    'License :: OSI Approved :: MIT License',

    # python 3 supported
    # 'Programming Language :: Python :: 3',
    # 'Programming Language :: Python :: 3.0',
    # 'Programming Language :: Python :: 3.1',
    # 'Programming Language :: Python :: 3.2',
    # 'Programming Language :: Python :: 3.3',
    # 'Programming Language :: Python :: 3.4',
    # 'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',

    # it's for a card game, right?
    'Topic :: Games/Entertainment'
]

# packages
PACKAGE_DIR = {'': 'src'}
PACKAGES = [
    'legendary',
    'legendary/buffy',
    'legendary/big_trouble'
]
PACKAGE_DATA = {
    'legendary': ['data/*.config']
}

# scripts
SCRIPTS = [
]

# the directory of this setup file
SETUP_DIR = os.path.abspath(os.path.dirname(__file__))

# where to find the version file; also where it will be written if it does not
# exist
VERSION_FILE = os.path.join(SETUP_DIR, 'src', 'legendary', 'version.py')

# version control file - this instructs the setup on how to dynamically
# increment the semantic version so the version.py file can be created and
# packaged with the distribution.
VERSION_CTRL_FILE = os.path.join(SETUP_DIR, 'version_ctrl.py')

# installation requirements
INSTALL_REQUIRES = open(os.path.join(SETUP_DIR, 'requirements.txt')).readlines()


def git_describe():
    '''
    Use 'git describe' to determine the current stable version
    '''
    # get the git describe value
    SETUP_LOGGER.info("Determining the version through git describe")
    proc = subprocess.Popen(["git", "describe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    # Error generally means there is not at least one annotated tag
    if err:
        SETUP_LOGGER.error(err)
        SETUP_LOGGER.error("Please make sure to create at least one annotated tag for this repo")
        sys.exit(1)

    # grab the description
    else:
        git_desc = out.decode().strip()
        SETUP_LOGGER.info("git describe: %s", git_desc)

    # pull the semantic version out of the git describe value
    version_match = re.search(r"^(\d+)\.(\d)\.(\d).*", git_desc)
    version_list = list(map(int, version_match.groups()))
    SETUP_LOGGER.info("Current version: %d.%d.%d", *version_list)
    return version_list

def write_version_file(new_version):
    '''
    Write the version.py file with the given version.
    '''
    # Create the version.py file
    SETUP_LOGGER.info("Opening %s and writing out version %s", VERSION_FILE, new_version)
    with open(VERSION_FILE, 'w') as vf_ref:
        vf_ref.write("'''\nVersion of CFAR Testing Harness Server\n'''\n\n__version__ = '{}'\n".format(new_version))

def version_check():
    '''
    Always run - check for the version file, produce it if not present.
    '''
    # if the version file does not already exist, create it
    if not os.path.exists(VERSION_FILE):
        # get the current version based on git describe
        current_version = git_describe()

        # import the increment_version function from the version control file
        spec = importlib.util.spec_from_file_location("version_control", VERSION_CTRL_FILE)
        version_ctrl_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version_ctrl_module)

        # use it to get the new version
        new_version = version_ctrl_module.increment_version(current_version)

        # format it as a sting and write it to file
        version = "{}.{}.{}".format(*new_version)
        SETUP_LOGGER.info("New version: %s", version)
        write_version_file(version)

# always run
version_check()

def get_version():
    '''
    Retrieve the version from the version.py file, which is assumed to already
    be in the src directory.
    '''
    SETUP_LOGGER.info("Retrieving version from version file %s", VERSION_FILE)
    spec = importlib.util.spec_from_file_location("version", VERSION_FILE)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return version_module.__version__

# call setup with our project-specific values
setup(
    name='legendary-chooser',
    version=get_version(),
    description='Choose a Legenary game setup',
    author='Edward Petersen',
    author_email="edward.petersen@gmail.com",
    url='https://github.com/timepieces141/legendary-chooser',
    license='MIT',
    platforms=['3'],
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    package_dir=PACKAGE_DIR,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    scripts=SCRIPTS,
    entry_points={
        'console_scripts': [
            'legendary = legendary.main:cli'
        ]
    }
)

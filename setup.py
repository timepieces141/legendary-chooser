'''
Build and distribute the Legendary Chooser!
'''
from codecs import open
import logging
import os
from setuptools import setup
import subprocess
import sys

# logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger('legendary-chooser')

# the setup_dir
setup_dir = os.path.abspath(os.path.dirname(__file__))

# packages
package_dir = {'': 'src'}
packages = [
    'legendary',
    'legendary/buffy'
]

# scripts
scripts = [
]

# classifications for this project - see
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    # project is in the alpha stage
    'Development Status :: 3 - Alpha',

    # MIT license
    'License :: OSI Approved :: MIT License',

    # python 3 supported
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',

    # palm trees are for entertainment
    'Topic :: Games/Entertainment'
]

# installation requirements
install_requires = open(os.path.join(setup_dir, 'requirements.txt'), mode='r', encoding='utf-8').readlines()

# where to find the version file; also where it will be written if it does not
# exist
version_file = os.path.join(setup_dir, 'src', 'version.py')

# parse the version from git, if not available
if not os.path.isfile(version_file):
    if '.git' in os.listdir(setup_dir):
        # git describe to grab the version
        logger.info("Determining the version through git describe")
        p = subprocess.Popen(["git", "describe", "--tags", "--abbrev=0"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()

        # Make sure the git version has at least one tag
        if err:
            logger.error("Error: You need to create at least one annotated tag for this repo")
            sys.exit(1)
        else:
            version = out.decode('utf-8').rstrip()
            logger.info("Version deterimined: %s", version)

            # Create the version.py file
            logger.info("Opening %s and writing version", version_file)
            with open(version_file, 'w', 'utf-8') as vf:
                vf.write("__version__ = '{0}'".format(version))


def get_version():
    '''
    retrieve the version from the version file
    '''
    d = {}
    with open(version_file, 'r', 'utf-8') as fp:
        # read in the key/value like it is a dictionary for easy access
        exec(compile(fp.read(), 'version.py', 'exec'), {}, d)
    return d['__version__']

# call setup with our project-specific values
setup(name='legendary-chooser',
      version=get_version(),
      description='Choose a Legenary game setup',
      author='Edward Petersen',
      author_email="edward.petersen@gmail.com",
      url='https://github.com/timepieces141/legendary-chooser',
      license='MIT',
      platforms=['3'],
      package_dir=package_dir,
      packages=packages,
      scripts=scripts,
      install_requires=install_requires
      )

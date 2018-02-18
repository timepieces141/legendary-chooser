'''
Tests for the legendary.main module.
'''

# testing imports
from click.testing import CliRunner
import pytest

# code under test
from legendary import main, version

@pytest.fixture(scope="module")
def runner():
    '''
    Click-specific command line interface runner.
    '''
    return CliRunner()

def test_cli_version(runner): # pylint: disable=redefined-outer-name
    '''
    Test the main cli can output the version.
    '''
    result = runner.invoke(main.cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == "Legendary Chooser\nversion {}\n".format(version.__version__)

'''
Tests for the legendary.main module.
'''

# core libraries
import logging

# testing imports
from click.testing import CliRunner
from click.exceptions import BadParameter
import pytest

# code under test
from legendary import main, version, util

# @pytest.fixture(scope="module")
@pytest.fixture()
def runner():
    '''
    Click-specific command line interface runner.
    '''
    return CliRunner()

@pytest.fixture()
def available_sets():
    '''
    Provides a mock function to replace the available_sets function in the util
    module.
    '''
    def mock_available_sets():
        '''
        The mock available_sets function.
        '''
        return ["buffy", "big_trouble"]

    return mock_available_sets

@pytest.mark.parametrize("sets,not_included",
                         [
                             (["foo"], ["foo"]),
                             (["foo", "buffy"], ["foo"]),
                             (["foo", "buffy", "big_trouble"], ["foo"]),
                             (["foo", "buffy", "big_trouble", "baz"], ["foo", "baz"]),
                             (["foo", "big_trouble", "baz"], ["foo", "baz"]),
                             (["foo", "buffy", "baz"], ["foo", "baz"]),
                             (["buffy"], []),
                             (["big_trouble"], []),
                             (["buffy", "big_trouble"], [])
                         ]
                        )
def test_validate_sets(available_sets, # pylint: disable=redefined-outer-name
                       monkeypatch, caplog, sets, not_included):
    '''
    Test the validate_sets function with various groupings of sets, some of
    which raise exceptions.
    '''
    # monkeypatch validate_sets's call to the available_sets utility function
    monkeypatch.setattr(util, "available_sets", available_sets)

    # if not_included has sets, then there will be an error
    caplog.set_level(logging.ERROR)
    if not_included:
        with pytest.raises(BadParameter):
            main.validate_sets(None, None, sets)
        for failed in not_included:
            assert "'{}' is not an available Legendary set.".format(failed) in caplog.text

    else:
        main.validate_sets(None, None, sets)

@pytest.mark.parametrize("var_available",
                         [
                             (["foo"]),
                             (["foo", "bar"]),
                             (["foo", "bar", "baz"]),
                         ]
                        )
def test_validate_sets_concat(monkeypatch, caplog, var_available):
    '''
    Test the specific logging line in the validate_sets function which properly
    concatenates the available sets, using commas and the word "and"
    appropriately.
    '''
    # define a mock available_sets that returns 1, 2, and 3 available sets
    def mock_available_sets():
        '''
        The mock available_sets function with a variable return depending on the
        values passed in by paramtrize.
        '''
        return var_available

    # monkeypatch validate_sets's call to the available_sets utility function
    monkeypatch.setattr(util, "available_sets", mock_available_sets)

    caplog.set_level(logging.ERROR)
    with pytest.raises(BadParameter):
        main.validate_sets(None, None, ["foobar"])

    # if only 1
    if len(var_available) == 1:
        assert "The available Legendary sets are: {}".format(var_available[0])

    # if two
    elif len(var_available) == 2:
        assert "The available Legendary sets are: {} and {}".format(var_available[0], var_available[1])

    # if three
    elif len(var_available) == 3:
        assert "The available Legendary sets are: {}, {} and {}".format(var_available[0],
                                                                        var_available[1],
                                                                        var_available[2])

def test_get_version():
    '''
    Test the version loaded by pkg_resource is the same as the version file that
    was written by the setup file.
    '''
    assert main.get_version() == version.__version__

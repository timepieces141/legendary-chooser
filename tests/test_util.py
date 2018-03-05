'''
Tests for the legendary.util module.
'''

# core libraries
import types
import importlib

# testing imports
import pytest

# code under test
from legendary import util

@pytest.fixture
def find_spec():
    '''
    Fixture that provides a mock find_spec method for monkkeypatching
    importlib.util.
    '''
    def mock_find_spec(name, package=None): # pylint: disable=unused-argument
        '''
        The mock method for monkeypatching importlib.util.
        '''
        loader = types.SimpleNamespace(exec_module=lambda module: "do nothing")
        return types.SimpleNamespace(loader=loader)

    return mock_find_spec

@pytest.fixture
def module_from_spec():
    '''
    Fixture that provides a mock module_from_spec method for monkkeypatching
    importlib.util.
    '''
    def mock_module_from_spec(spec): # pylint: disable=unused-argument
        '''
        The mock method for monkeypatching importlib.util.
        '''
        return "foobar"

    return mock_module_from_spec

def test_get_package_from_name_already_loaded(monkeypatch):
    '''
    Test the get_package_from_name function where the package has already been
    loaded for the name given.
    '''
    test_values = ("foobar", "foobar")
    monkeypatch.setattr(util, "_LOADED_PACKAGES", {test_values[0]: test_values[1]})
    assert test_values[1] == util.get_package_from_name(test_values[0])

def test_get_package_from_name_bad_set():
    '''
    Test the get_package_from_name function where the given legendary set
    (package) does not exist. Expect it to raise a AttributeError error, when
    importlib.util.module_from_spec receives None (from the call to
    importlib.util.find_spec).
    '''
    for bad_arg in ["foobar", None]:
        with pytest.raises(AttributeError):
            util.get_package_from_name(bad_arg)

def test_get_package_from_name_success(monkeypatch, find_spec, module_from_spec): # pylint: disable=redefined-outer-name
    '''
    Test the get_package_from_name function where the given legendary set
    (package) is valid. Here we monkeypatch the actual loading of the module, as
    we need not test importlib, just that
    '''
    # monkeypatch a few things
    monkeypatch.setattr(importlib.util, "find_spec", find_spec)
    monkeypatch.setattr(importlib.util, "module_from_spec", module_from_spec)

    # test - the first time runs through the loading code, the second that what
    # was saved to state remains and is correct
    assert util.get_package_from_name("foobar") == "foobar"
    assert util.get_package_from_name("foobar") == "foobar"

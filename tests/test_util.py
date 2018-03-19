'''
Tests for the legendary.util module.
'''

# core libraries
import importlib
import logging
import os
import types

# third party libraries
from appdirs import user_data_dir

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

def test_get_package_from_name_success(find_spec, module_from_spec, # pylint: disable=redefined-outer-name
                                       monkeypatch):
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

def test_create_directory(fs, # pylint: disable=invalid-name, unused-argument
                          caplog):
    '''
    Test the create_directory function where the target directory does not
    exist. Ensure that when it does exist, nothing bad happens.
    '''
    # call _create_data_directory when it does not exist, verify that it was
    # created in the fake filesystem
    data_dir = user_data_dir("legendary", "Edward Petersen")
    assert not os.path.exists(data_dir)
    caplog.set_level(logging.DEBUG)
    util.create_directory(data_dir) # pylint: disable=protected-access
    assert "Created the directory at: {}".format(data_dir) in caplog.text
    assert os.path.exists(data_dir)

    # call it again now that the directory exists, to hit the exception (that
    # ignores it)
    util.create_directory(data_dir) # pylint: disable=protected-access
    assert "Directory '{}' already exists".format(data_dir) in caplog.text

def test_create_directory_no_permission(fs): # pylint: disable=invalid-name
    '''
    Test the create_directory function where the target directory to create
    cannot be created for a reason *other* than that it already exists - here,
    specifically, we use bad permissions.
    '''
    # create the parent directory to the user data directory in the fake file
    # system, but with harsh permissions, so as to see the raised exception that
    # *isn't* EEXIST
    data_dir = user_data_dir("legendary", "Edward Petersen")
    parent_dir = os.path.dirname(data_dir)
    fs.CreateDirectory(parent_dir, 0o444)
    with pytest.raises(PermissionError):
        util.create_directory(data_dir) # pylint: disable=protected-access

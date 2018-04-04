'''
Tests for the legendary.util module.
'''
# core libraries
import json
import logging
import os

# testing imports
import pytest

# third party libraries
# from appdirs import user_data_dir

# code under test
from legendary import util
from legendary.util import USER_DATA_DIR, SETS_DIR
from legendary.exceptions import InitializationError

def test_create_directory(fs, # pylint: disable=invalid-name, unused-argument
                          caplog):
    '''
    Test the create_directory function where the target directory does not
    exist. Ensure that when it does exist, nothing bad happens.
    '''
    # call _create_data_directory when it does not exist, verify that it was
    # created in the fake filesystem
    assert not os.path.exists(USER_DATA_DIR)
    caplog.set_level(logging.DEBUG)
    util.create_directory(USER_DATA_DIR)
    assert "Created the directory at: {}".format(USER_DATA_DIR) in caplog.text
    assert os.path.exists(USER_DATA_DIR)

    # call it again now that the directory exists, to hit the exception (that
    # ignores it)
    util.create_directory(USER_DATA_DIR)
    assert "Directory '{}' already exists".format(USER_DATA_DIR) in caplog.text

def test_create_directory_no_permission(fs): # pylint: disable=invalid-name
    '''
    Test the create_directory function where the target directory to create
    cannot be created for a reason *other* than that it already exists - here,
    specifically, we use bad permissions.
    '''
    # create the parent directory to the user data directory in the fake file
    # system, but with harsh permissions, so as to see the raised exception that
    # *isn't* EEXIST
    assert not os.path.exists(USER_DATA_DIR)
    parent_dir = os.path.dirname(USER_DATA_DIR)
    assert not os.path.exists(parent_dir)
    fs.CreateDirectory(parent_dir, 0o444)
    assert os.path.exists(parent_dir)
    with pytest.raises(PermissionError):
        util.create_directory(USER_DATA_DIR)

@pytest.mark.parametrize("dir_name", ["", "sets"])
def test_restore_file_bad_permission_dest(fs, # pylint: disable=invalid-name
                                          caplog, dir_name):
    '''
    Test the restore_file function where user data directory (and later the
    "sets" directory) cannot be created because it's parent directory is
    unwritable.
    '''
    # path to the directory under test
    target_dir = os.path.join(USER_DATA_DIR, dir_name)
    assert not os.path.exists(target_dir)

    # create the parent with restricted permissions
    parent_dir = os.path.dirname(target_dir)
    assert not os.path.exists(parent_dir)
    fs.CreateDirectory(parent_dir, 0o444)
    assert os.path.exists(parent_dir)

    # test we raise an exception
    caplog.set_level(logging.WARNING)
    with pytest.raises(InitializationError):
        util.restore_file("doesn't_matter")
    assert "Directory '{}' is inaccessible because of a permissions error".format(parent_dir) in caplog.text

def test_restore_file_bad_src_filesystem_structure(fs): # pylint: disable=invalid-name
    '''
    Test the restore_file function where the user data directory cannot be
    created for a reason *other* than the permissions error tested above - here
    we use that the parent "directory" already exists as a file.
    '''
    # create the parent directory as a *file*
    parent_dir = os.path.dirname(USER_DATA_DIR)
    assert not os.path.exists(parent_dir)
    fs.CreateFile(parent_dir)
    assert os.path.exists(parent_dir)

    # test we raise an exception
    with pytest.raises(NotADirectoryError):
        util.restore_file("doesn't_matter")

def test_restore_file_no_orig(fs, # pylint: disable=invalid-name, unused-argument
                              caplog):
    '''
    Test the restore_file function where the source config file does not exist
    for copying to the user data directory.
    '''
    # the dummy (source) config file
    import pkg_resources
    dummy_set = "foobar"
    config = pkg_resources.resource_filename("legendary", os.path.join("data", "{}.config".format(dummy_set)))

    # test that we raise an exception when that file does not exist
    caplog.set_level(logging.WARNING)
    with pytest.raises(InitializationError):
        util.restore_file(dummy_set)

    # assert the logging of the error
    assert "Source configuration file '{}' for Legendary set '{}' does not " \
           "exist!".format(config, dummy_set) in caplog.text

def test_restore_file_cant_overwrite(fs, # pylint: disable=invalid-name
                                     caplog):
    '''
    Test the restore_file function where the destination config file location is
    not writable.
    '''
    # the source config file
    import pkg_resources
    real_set = "buffy"
    config = pkg_resources.resource_filename("legendary", os.path.join("data", "{}.config".format(real_set)))
    assert not os.path.exists(config)
    fs.CreateFile(config)
    assert os.path.exists(config)

    # create the file in the sets sub-directory of the user's data directory,
    # but make it unwritable
    dst_file = os.path.join(SETS_DIR, "buffy.config")
    assert not os.path.exists(dst_file)
    fs.CreateFile(dst_file, 0o444)
    assert os.path.exists(dst_file)

    # test that we raise an exception when destination file is unwritable
    caplog.set_level(logging.WARNING)
    with pytest.raises(InitializationError):
        util.restore_file(real_set)

    # assert the logging of the error
    assert "Destination configuraion file '{}' for Legendary set '{}' inaccessible because of a permissions " \
           "error".format(dst_file, real_set) in caplog.text

def test_restore_file_bad_dst_filesystem_structure(fs, # pylint: disable=invalid-name
                                                   monkeypatch):
    '''
    Test the restore_file function where copying the config file cannot be done
    for a reason *other* than the two errors tested above - here we use that the
    sets "directory" already exists as a *file*.
    '''
    # monkeypatch the create_directory function to get past
    monkeypatch.setattr(util, "create_directory", lambda directory: None)

    # create the "sets" directory as a *file*
    assert not os.path.exists(SETS_DIR)
    fs.CreateFile(SETS_DIR)
    assert os.path.exists(SETS_DIR)

    # the source config file
    import pkg_resources
    real_set = "buffy"
    config = pkg_resources.resource_filename("legendary", os.path.join("data", "{}.config".format(real_set)))
    assert not os.path.exists(config)
    fs.CreateFile(config)
    assert os.path.exists(config)

    # test we raise an exception
    with pytest.raises(NotADirectoryError):
        util.restore_file(real_set)

def test_restore_file_success(fs, # pylint: disable=invalid-name
                              caplog):
    '''
    Test the restore_file function, expecting a successful copy.
    '''
    # the source config file
    import pkg_resources
    real_set = "buffy"
    config = pkg_resources.resource_filename("legendary", os.path.join("data", "{}.config".format(real_set)))
    assert not os.path.exists(config)
    fs.CreateFile(config)
    assert os.path.exists(config)

    # test copying the file when it doesn't previously exist
    caplog.set_level(logging.DEBUG)
    util.restore_file(real_set)

    # assert the success is logged and the file is copied
    assert "Configuration file for Legendary set '{}' restored!".format(real_set) in caplog.text
    assert os.path.exists(os.path.join(SETS_DIR, "{}.config".format(real_set)))

    # test copying the file again, overwriting
    util.restore_file(real_set)

    # assert the success is logged
    assert "Configuration file for Legendary set '{}' restored!".format(real_set) in caplog.text

def test_initialize_already_exists(fs, # pylint: disable=invalid-name
                                   caplog):
    '''
    Test the initialize function where the initialized file already exists.
    '''
    # create the init file
    init_file = os.path.join(USER_DATA_DIR, ".initialized")
    assert not os.path.exists(init_file)
    fs.CreateFile(init_file)
    assert os.path.exists(init_file)

    # test the function
    caplog.set_level(logging.DEBUG)
    util.initialize()
    assert "Initialization file exists, skipping ..." in caplog.text

def test_initialize_restoring_file_exception(fs, # pylint: disable=invalid-name, unused-argument
                                             monkeypatch):
    '''
    Test the initialize function where the calls to the restore_file function
    produce an exception.
    '''
    # monkeypatch the restore_file function, we test that elsewhere
    monkeypatch.setattr(util, "restore_file", lambda legendary_set: (_ for _ in ()).throw(InitializationError()))

    # call initialize, skipping the check (tests that as well), with an empty
    # filesystem - should raise and exception
    with pytest.raises(InitializationError):
        util.initialize(False)

    # assert the intialized file hasn't been written
    init_file = os.path.join(USER_DATA_DIR, ".initialized")
    assert not os.path.exists(init_file)

def test_initialize_cant_write_init_file(fs, # pylint: disable=invalid-name
                                         caplog, monkeypatch):
    '''
    Test the initialize function where we can't write the initialized file.
    '''
    # monkeypatch the restore_file function, we test that elsewhere
    monkeypatch.setattr(util, "restore_file", lambda legendary_set: None)

    # since the calls to restore_file would create and/or verify that the user
    # data directory exists and is writable, the only error we need to control
    # for is if the .initialized file already exists but
    init_file = os.path.join(USER_DATA_DIR, ".initialized")
    fs.CreateFile(init_file, 0o444)

    # test that we get an exception
    caplog.set_level(logging.ERROR)
    with pytest.raises(InitializationError):
        util.initialize(False)
    assert "The initialization file cannot be written because of a file system permission error." in caplog.text

def test_initialize_bad_dst_filesystem_structure(fs, # pylint: disable=invalid-name, unused-argument
                                                 monkeypatch):
    '''
    Test the initialize function where we can't write the initialized file for a
    reason *other* that those already tested - here, specifically, we use the
    user data directory not existing (which would actually never happen).
    '''
    # monkeypatch the restore_file function, we test that elsewhere
    monkeypatch.setattr(util, "restore_file", lambda legendary_set: None)

    # test expecting an exception
    with pytest.raises(FileNotFoundError):
        util.initialize(False)

def test_initialize_success(fs, # pylint: disable=invalid-name
                            caplog, monkeypatch):
    '''
    Test the initialize function, expecting success and the intiailzed file to
    be written.
    '''
    # monkeypatch the restore_file function, we test that elsewhere
    monkeypatch.setattr(util, "restore_file", lambda legendary_set: None)

    # create the user's data directory
    fs.CreateDirectory(USER_DATA_DIR)

    # test initialized file is created
    caplog.set_level(logging.DEBUG)
    init_file = os.path.join(USER_DATA_DIR, ".initialized")
    assert not os.path.exists(init_file)
    util.initialize()

    # assert it was created
    assert os.path.exists(init_file)
    assert "Initialization file written" in caplog.text

    # TODO: test the contents of the initialized file

@pytest.mark.parametrize("configs,expected,skipped,invalids",
                         [
                             ({}, [], [], []),
                             ({"buffy.config": {"x": "y"}, "big_trouble.config": {"x": "y"}, "foobar": "foobar"},
                              ["buffy", "big_trouble"],
                              ["foobar"],
                              []),
                             ({"buffy.config": {"x": "y"}, "big_trouble.config": None, "foobar": "foobar"},
                              ["buffy"],
                              ["foobar"],
                              ["big_trouble.config"]),
                         ]
                        ) # pylint: disable=invalid-name, too-many-arguments
def test_available_sets(fs,
                        configs, expected, skipped, invalids, caplog):
    '''
    Test the available_sets function with various inputs that tickle both the
    file extension and the valid json filtering.
    '''
    # first create the user "sets" directory
    fs.CreateDirectory(SETS_DIR)

    # create the files designated by the configs argument
    for config, contents in configs.items():
        file_path = os.path.join(SETS_DIR, config)
        if contents:
            fs.CreateFile(file_path, contents=json.dumps(contents))
        else:
            fs.CreateFile(file_path)

    # grab the available sets
    caplog.set_level(logging.DEBUG)
    available = util.available_sets()
    assert set(available) == set(expected)

    # check the skipped
    for not_used in skipped:
        assert "'{}' is not a appropriately named as a configuration file, skipping...".format(not_used) in caplog.text

    # check the invalid
    for invalid in invalids:
        assert "'{}' is not a valid configuration file, skipping...".format(invalid) in caplog.text






# @pytest.fixture
# def find_spec():
#     '''
#     Fixture that provides a mock find_spec method for monkkeypatching
#     importlib.util.
#     '''
#     def mock_find_spec(name, package=None): # pylint: disable=unused-argument
#         '''
#         The mock method for monkeypatching importlib.util.
#         '''
#         loader = types.SimpleNamespace(exec_module=lambda module: "do nothing")
#         return types.SimpleNamespace(loader=loader)

#     return mock_find_spec

# @pytest.fixture
# def module_from_spec():
#     '''
#     Fixture that provides a mock module_from_spec method for monkkeypatching
#     importlib.util.
#     '''
#     def mock_module_from_spec(spec): # pylint: disable=unused-argument
#         '''
#         The mock method for monkeypatching importlib.util.
#         '''
#         return "foobar"

#     return mock_module_from_spec

# def test_get_package_from_name_already_loaded(monkeypatch):
#     '''
#     Test the get_package_from_name function where the package has already been
#     loaded for the name given.
#     '''
#     test_values = ("foobar", "foobar")
#     monkeypatch.setattr(util, "_LOADED_PACKAGES", {test_values[0]: test_values[1]})
#     assert test_values[1] == util.get_package_from_name(test_values[0])

# def test_get_package_from_name_bad_set():
#     '''
#     Test the get_package_from_name function where the given legendary set
#     (package) does not exist. Expect it to raise a AttributeError error, when
#     importlib.util.module_from_spec receives None (from the call to
#     importlib.util.find_spec).
#     '''
#     for bad_arg in ["foobar", None]:
#         with pytest.raises(AttributeError):
#             util.get_package_from_name(bad_arg)

# def test_get_package_from_name_success(find_spec, module_from_spec, # pylint: disable=redefined-outer-name
#                                        monkeypatch):
#     '''
#     Test the get_package_from_name function where the given legendary set
#     (package) is valid. Here we monkeypatch the actual loading of the module, as
#     we need not test importlib, just that
#     '''
#     # monkeypatch a few things
#     monkeypatch.setattr(importlib.util, "find_spec", find_spec)
#     monkeypatch.setattr(importlib.util, "module_from_spec", module_from_spec)

#     # test - the first time runs through the loading code, the second that what
#     # was saved to state remains and is correct
#     assert util.get_package_from_name("foobar") == "foobar"
#     assert util.get_package_from_name("foobar") == "foobar"

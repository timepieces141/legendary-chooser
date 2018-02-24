'''
Random utilities that are used across many legendary modules.
'''

# core libraries
import importlib

# packages already loaded
_LOADED_PACKAGES = {}

def get_package_from_name(legendary_set):
    '''
    Given a legendary set name, import the package that holds all of its config,
    and return a reference to it.
    '''
    # skip if already loaded
    global _LOADED_PACKAGES
    if legendary_set in _LOADED_PACKAGES:
        return _LOADED_PACKAGES[legendary_set]

    # load it
    spec = importlib.util.find_spec(legendary_set)
    set_package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(set_package)
    _LOADED_PACKAGES[legendary_set] = set_package
    return set_package

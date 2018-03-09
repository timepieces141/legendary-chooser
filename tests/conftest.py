'''
Testing configuration file - provides fixtures, etc.
'''

# core libraries
from enum import Enum
import itertools

# testing imports
import pytest

@pytest.fixture
def card_group_enum():
    '''
    Mock card group enumeration, just like the ones found in the set-specific
    types module.
    '''
    card_groups = {
        1: ["Foo", "FOO"],
        2: ["Bar", "BAR"],
        3: ["Baz", "BAZ"],
        4: ["Foobar", "FOOBAR"],
    }
    fake_card_groups = Enum(
        value="CardGroup",
        names=itertools.chain.from_iterable(
            itertools.product(v, [k]) for k, v in card_groups.items()
        )
    )
    return fake_card_groups

'''
Tests for the legendary.exceptions module.
'''

# code under test
from legendary.exceptions import LegendaryError


def test_le_error(caplog):
    '''
    Tests the construction and logging of the base exception
    LegendaryError.
    '''
    LegendaryError()
    assert "LegendaryError should not be used long term - it should be a placeholder " \
           "for an exception yet to be defined" in caplog.text

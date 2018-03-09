'''
Error and Exception definitions.
'''

# core libraries
import logging

class LegendaryError(Exception):
    '''
    The parent error for all errors raised in the legendary-chooser code base.
    Also the stand-in error in cases for which a concrete, detailed error has
    not yet been defined.
    '''
    def __init__(self, message=None):
        if type(self) is LegendaryError: # pylint: disable=unidiomatic-typecheck
            logging.warning("LegendaryError should not be used long term - it should be a placeholder for an " \
                            "exception yet to be defined")
        super(LegendaryError, self).__init__(message)

class ConfigurationError(LegendaryError):
    '''
    Exception raised when there is an error in the configruration process.
    '''
    pass

class ValidationError(ConfigurationError):
    '''
    Exception raised when there is an error in the validation process, usually
    due to premature validation.
    '''
    pass

'''
This directs the automatic version bumping as to what portions of the version
should be bumped, and by how much, upon the next successful build.
'''

# core libraries
from enum import Enum

class VersionBump(Enum):
    '''
    The portion of the semantic version to bump.
    '''
    UPDATE = "UPDATE"
    MINOR = "MINOR"
    MAJOR = "MAJOR"


# The global control variable - only ONE should be uncommented at a time; UPDATE
# is last just in case more than one is uncommented, as it is the safest version
# bump (and the default)
# VERSION_BUMP = VersionBump.MAJOR
# VERSION_BUMP = VersionBump.MINOR
VERSION_BUMP = VersionBump.UPDATE


def increment_version(version):
    '''
    Updates the given version, given as a tuple of (major, minor, update) based
    on the value dictated in this control file, as defined by the global
    VERSION_BUMP which is a value of the Enum VersionBump. VersionBump.UPDATE
    causes a simple increment of the update portion of the version.
    VersionBump.MINOR causes an increment of the minor portion of the version,
    and a zero-out of the update portion. And finally, VersionBump.MAJOR causes
    an increment of the major portion of the version, and a zero-out of both the
    update portion and the minor port.
    '''
    if VERSION_BUMP is VersionBump.MAJOR:
        version = (version[0] + 1, 0, 0)
    elif VERSION_BUMP is VersionBump.MINOR:
        version = (version[0], version[1] + 1, 0)
    else:
        version = (version[0], version[1], version[2] + 1)
    return version

# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)

"""Custom exceptions for the compose-to-quadlet project."""

class ComposeToQuadletError(Exception):
    """Base exception for all errors in compose-to-quadlet."""
    pass

class VersionNotFoundError(ComposeToQuadletError):
    """Raised when a version string cannot be found in a file."""
    pass

class VersionMismatchError(ComposeToQuadletError):
    """Raised when version strings across different files do not match."""
    pass

class ComposeParsingError(ComposeToQuadletError):
    """Raised when there is an error parsing the Compose YAML."""
    pass
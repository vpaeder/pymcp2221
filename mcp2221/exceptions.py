"""Exceptions and warnings for MCP2221 driver."""

__all__ = ["FailedCommandException", "IOException", "InvalidParameterException", "InvalidReturnValueWarning"]

class MCPException(Exception):
    """Base class for custom exceptions."""
    pass

class FailedCommandException(MCPException):
    """This is used to notify that a command was issued and has failed."""
    pass

class IOException(MCPException):
    """This tells that one couldn't access the device."""
    pass

class InvalidParameterException(MCPException):
    """This should be triggered when a command parameter is invalid."""
    pass

class MCPWarning(Warning):
    """Base class for custom warnings."""
    pass

class InvalidReturnValueWarning(MCPWarning):
    """This is used to mention that the chip returned an invalid value."""
    pass

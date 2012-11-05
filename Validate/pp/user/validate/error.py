# -*- coding: utf-8 -*-
"""
This contains for general exceptions.
"""


class UserNotFoundError(Exception):
    """Raised when a user was not found."""


class CommunicationError(Exception):
    """A server error occured adding performing an operation."""

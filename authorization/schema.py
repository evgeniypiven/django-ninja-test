"""
Authorization Schema
"""
# Standard library imports.

# Related third party imports.
from ninja import Schema

# Local application/library specific imports.


class RegistrationSchema(Schema):
    username: str
    email: str
    password: str


class LoginSchema(Schema):
    username: str
    password: str


class AuthorizationResponseSchema(Schema):
    message: str
    token: str

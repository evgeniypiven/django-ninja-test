"""
Authorization API Urls
"""

# Standard library imports.


# Related third party imports.
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from ninja import NinjaAPI

# Local application/library specific imports.
from .schema import (
    RegistrationSchema,
    LoginSchema,
    AuthorizationResponseSchema,
)
from starnavi.schema import Error
from .models import CustomUser


api = NinjaAPI(urls_namespace='authorization',
               version="1.0.0",
               title="Authorization API")


@api.post("/register", response={201: AuthorizationResponseSchema, 401: Error})
def registration(request, user_info: RegistrationSchema):
    """
    User registration.

    Request parameters(body):
    - name: username
    - type: String
    - description: username

    - name: email
    - type: String
    - description: email

    - name: password
    - type: String
    - description: password

    Response parameters(JSON):
    - name: message
    - type: String
    - description: description of request result

    - name: token
    - type: String
    - description: uses for authentication

    Response status(int):
        - 201 - success. created
        - 401 - fail. wrong parameters
    """
    # Check if username or email already exist
    if CustomUser.objects.filter(username=user_info.username).exists():
        return 401, {"message": "Username already taken"}

    if CustomUser.objects.filter(email=user_info.email).exists():
        return 401, {"message": "Email already registered"}

    # Create the user
    user = CustomUser.objects.create_user(
        username=user_info.username,
        email=user_info.email,
    )
    user.set_password(user_info.password)
    user.save()

    token = Token.objects.create(user=user)

    return 201, {"message": "User created successfully", "token": token.key}


@api.post("/login", response={200: AuthorizationResponseSchema, 401: Error})
def login(request, login_info: LoginSchema):
    """
    User login.

    Request parameters(body):
    - name: username
    - type: String
    - description: username

    - name: password
    - type: String
    - description: password

    Response parameters(JSON):
    - name: message
    - type: String
    - description: description of request result

    - name: token
    - type: String
    - description: uses for authentication

    Response status(int):
        - 200 - success. created
        - 401 - fail. wrong parameters
    """
    user = authenticate(username=login_info.username, password=login_info.password)

    if user is not None:
        # Authentication successful, generate token and return
        token = user.auth_token.key  # Assuming you are using Token Authentication
        return 200, {"message": f"Logged in successfully as {user.username}", "token": token}
    else:
        return 401, {"message": "Invalid credentials"}

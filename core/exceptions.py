from rest_framework import status
from rest_framework.exceptions import APIException


class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}


class BaseCustomAPIException(APIException):
    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class BadRequestException(BaseCustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"
    default_code = "invalid"


class UnauthorizedException(BaseCustomAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized"
    default_code = "unauthorized"


class ConversionError(Exception):
    pass


class NotFoundException(APIException):
    def __init__(self, Klass, *, verbose=False, id=None):
        self.klass = Klass
        self.status_code = status.HTTP_404_NOT_FOUND
        if verbose and id:
            self.detail = f"{self.klass.__name__} with id '{id}' not found"
        else:
            self.detail = f"{self.klass.__name__} not found"


class UnauthenticatedOnly(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "User is authenticated."
    default_code = "unauthenticated_only"

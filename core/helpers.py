from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404 as g_404
from django.utils import timezone

from core.exceptions import NotFound


def response_dict(message: str, data: dict = None) -> dict:
    if data is None:
        data = {}
    response = {"message": message}
    if data:
        response["data"] = data
    return response


def make_aware(naive_datetime):
    return timezone.make_aware(naive_datetime, timezone.get_current_timezone())


def get_object_or_404(Klass, verbose=False, *args, **kwargs):
    """A custom get_object_or_404 function
    that customizes the not found message"""
    try:
        return g_404(Klass, *args, **kwargs)
    except Http404:
        if isinstance(Klass, models.Manager) or isinstance(Klass, models.QuerySet):
            Klass = Klass.model

        if verbose:
            raise NotFound(Klass=Klass, verbose=True, id=kwargs.get("id"))
        else:
            raise NotFound(Klass=Klass)

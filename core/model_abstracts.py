import uuid

from django.db import models
from django_extensions.db.models import TimeStampedModel


class Model(TimeStampedModel, models.Model):
    """Model \n
    An abstract base model that provides a UUID field.
    """

    uid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

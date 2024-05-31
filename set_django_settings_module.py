import os

from iswift.settings import base

if base.DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iswift.settings.development")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iswift.settings.production")

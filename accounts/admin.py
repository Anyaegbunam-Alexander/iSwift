from django.contrib import admin

from accounts.models import OTP, User

admin.site.register(User)
admin.site.register(OTP)

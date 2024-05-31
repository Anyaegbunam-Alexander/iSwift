from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

from accounts.models import User

password_reset_token = PasswordResetTokenGenerator()


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: User, timestamp: int) -> str:
        return text_type(user.uid) + text_type(timestamp) + text_type(user.has_verified_email)


email_activation_token = EmailVerificationTokenGenerator()

import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from accounts.models import OTP, User
from core.exceptions import BadRequestException, NotFoundException
from core.helpers import response_dict


def send_otp(phone_number, otp) -> dict:
    # Send an SMS message
    # message = f"Your iSwift code is {otp}"
    # url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_ID}/messages"
    # headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    # body = {
    #     "messaging_product": "whatsapp",
    #     "recipient_type": "individual",
    #     "to": f"+234{phone_number[1:]}",
    #     "type": "text",
    #     "text": {
    #         "preview_url": False,
    #         "body": message,
    #     },
    # }
    # response = requests.post(url=url, json=body, headers=headers)

    # if response.status_code == 200:
    #     data = "Successfully sent OTP"
    # else:
    #     # Log the error details for debugging
    #     logging.error(f"Failed to send OTP: {response.content}")
    #     # Return a generic error message
    #     data = "Failed to send OTP. Please try again later."

    data = "Successfully sent OTP"
    return {"data": response_dict(data), "status": 200}


class OTPGenerator:
    def __init__(self, data: dict, activate_user=False):
        """
        Initializes the OTPGenerator class
        with the given data and activate_user parameters.

        Args:
            data: A dictionary containing the input data.
            activate_user: A boolean indicating whether to activate the user's account.
        """
        self.data = data
        self.activate_user = activate_user
        self.max_out_minutes = settings.OTP_MAX_OUT_MINUTES
        self.expiry_minutes = settings.OTP_EXPIRY_MINUTES

    def generate_otp(self) -> dict:
        """
        Generates an OTP for the given user
        and updates their OTP information in the database.

        Returns:
            `True` if otp generation is successful
        """

        # Retrieve the phone number from the input data
        phone_number = self.data.get("phone_number")

        # Get the user instance associated with the phone number
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            raise NotFoundException(User)
        # If activate_user is True and the user is already active, raise an exception
        if self.activate_user and user.is_active:
            raise PermissionDenied("Not Allowed")

        # Get the user's OTP information from the database
        user_otp = OTP.objects.filter(user=user).first()
        if not user_otp:
            raise NotFoundException(User)

        # If the user has reached the maximum number of OTP tries, raise an exception
        if not self._can_generate_otp(user_otp):
            message = f"Max OTP try reached. Try again after {self.max_out_minutes} minutes"
            raise BadRequestException(message, status_code=status.HTTP_400_BAD_REQUEST)

        # Generate a new OTP
        otp = OTP.generate_otp()

        # Set the OTP expiry time
        otp_expiry = timezone.now() + datetime.timedelta(minutes=self.expiry_minutes)

        # Decrement the max_otp_try counter
        max_otp_try = int(user_otp.max_otp_try) - 1

        # Update the user's OTP information in the database
        user_otp.otp = otp
        user_otp.otp_expiry = otp_expiry
        user_otp.max_otp_try = max_otp_try

        # Update the user's OTP information based on the value of max_otp_try
        self._update_user_otp(user_otp, max_otp_try)

        # TODO: complete send_otp function
        return send_otp(user.phone_number, otp)

    def _can_generate_otp(self, user_otp: OTP):
        """
        Checks if an OTP can be generated for the given user.

        Args:
            user_otp: An instance of the OTP model.

        Returns:
            `True` if an OTP can be generated, `False` otherwise.
        """

        # Check if the user has reached the maximum number
        # of OTP tries or if they are in a cool down period.
        return not (int(user_otp.max_otp_try) == 0 and timezone.now() < user_otp.otp_max_out)

    def _update_user_otp(self, user_otp: OTP, max_otp_try):
        """
        Updates the given user's OTP information in the database.

        Args:
            user_otp: An instance of the OTP model.
            max_otp_try: The current value of the max_otp_try counter.
        """

        # If max_otp_try is 0, set a cool down time for generating new OTPs.
        if max_otp_try == 0:
            # Set cool down time
            otp_max_out = timezone.now() + datetime.timedelta(minutes=self.max_out_minutes)
            user_otp.otp_max_out = otp_max_out

        # If max_otp_try is -1, reset it to its initial value.
        elif max_otp_try == -1:
            user_otp.max_otp_try = settings.MAX_OTP_TRY

        # Otherwise, update max_otp_try and reset otp_max_out to None.
        else:
            user_otp.otp_max_out = None
            user_otp.max_otp_try = max_otp_try

        # save changes to database.
        user_otp.save()


class OTPVerifier:
    def __init__(self, data: dict, activate_user=False):
        """
        Initializes the OTPVerifier class with the
        given data and activate_user parameters.

        Args:
            data: A dictionary containing the input data.
            activate_user: A boolean indicating
            whether to activate the user's account.
        """
        self.data = data
        self.activate_user = activate_user
        self.invalid_otp_message = "Expired or incorrect OTP"

    def verify_otp(self) -> User:
        """
        Verifies the given OTP and updates
        the user's OTP information in the database.

        Returns:
            A User instance
        """
        # Retrieve the otp and phone number from the input data
        otp = self.data.get("otp")
        phone_number = self.data.get("phone_number")

        # Get the user's OTP information from the database
        user_otp = OTP.objects.filter(otp=otp).first()

        # If no matching OTP is found, raise an exception
        if not user_otp:
            raise BadRequestException(self.invalid_otp_message, status.HTTP_400_BAD_REQUEST)

        # Get the user instance associated with the phone number
        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise BadRequestException(self.invalid_otp_message, status.HTTP_400_BAD_REQUEST)

        # If the user and user_otp.user instances do not match, raise an exception
        if user != user_otp.user:
            raise BadRequestException(self.invalid_otp_message, status.HTTP_400_BAD_REQUEST)

        # If activate_user is True and the user is already active, raise an exception
        if self.activate_user and user.is_active:
            raise BadRequestException(self.invalid_otp_message, status.HTTP_400_BAD_REQUEST)

        # If the OTP is not valid, raise an exception
        if not self._is_valid_otp(user_otp):
            raise BadRequestException(self.invalid_otp_message, status.HTTP_400_BAD_REQUEST)

        # Update the user's OTP information in the database
        self._update_user_otp(user_otp)

        # If activate_user is True and a user instance exists, activate the user's account
        if self.activate_user and user:
            user.is_active = True
            user.save()

        return user

    def _is_valid_otp(self, user_otp: OTP):
        """
        Checks if the given OTP is valid.

        Args:
            user_otp: An instance of the OTP model.

        Returns:
            `True` if the OTP is valid, `False` otherwise.
        """

        # Check if the OTP has not expired.
        return user_otp.otp_expiry and timezone.now() < user_otp.otp_expiry

    def _update_user_otp(self, user_otp: OTP):
        """
        Updates the given user's OTP information in the database.

        Args:
            user_otp: An instance of the OTP model.
        """

        # Reset otp_expiry and max_out_try to their initial values.
        # Set otp_max_out to None.
        user_otp.otp_expiry = None
        user_otp.max_otp_try = settings.MAX_OTP_TRY
        user_otp.otp_max_out = None

        # Save changes to database.
        user_otp.save()

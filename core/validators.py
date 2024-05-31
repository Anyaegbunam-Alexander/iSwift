from django.core.validators import RegexValidator

# TODO expand to include other country number lengths
phone_regex = RegexValidator(regex=r"^\d{11}", message="Phone number must be 11 digits only.")

country_code_regex = RegexValidator(
    regex=r"^\d{1,4}", message="Country code must be more than 1 digit and not more than 4 digits."
)

account_number_regex = RegexValidator(
    regex=r"^\d{10}", message="Phone number must be 10 digits only."
)
otp_regex = RegexValidator(regex=r"^\d{6}$", message="OTP must be 6 digits only.")

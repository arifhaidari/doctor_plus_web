from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.validators import FileExtensionValidator
from datetime import datetime


# Model validations for Models, ModelForms and ModelSerializers
def name(value):
    name = str(value)
    if any(not c.isalpha() for c in name.replace(" ", "")):
        raise ValidationError("Name Should only contain letters.")
    return value


def phone_number(value):
    phone_number = str(value)
    if not phone_number.isnumeric():
        raise ValidationError("Phone Field Should only contain numbers.", code=None, params=None)
    if len(phone_number) > 13 or len(phone_number) < 10:
        raise ValidationError("Phone Number length is incorrect.(10-13)")
    return value


def dob(value):
    dob = str(value)
    dob = datetime.strptime(dob, "%Y-%m-%d")
    now = datetime.now()
    if dob.date() >= now.date():
        raise ValidationError("Date of birth can not be greater or equal to current date.")
    return value


def avatar_size(value):
    image_max_size = 2.0  # MB
    file_size = value.size
    if file_size > image_max_size * 1024 * 1024:
        # messages.warning(request, "Refresh your page and submit your ule")
        raise ValidationError(f"Image size can not be greater then {image_max_size}MB.")
    return value


avatar_type = FileExtensionValidator(["png", "jpg", "jpeg", "tiff", "tif", "bmp"], message="Invalid Image extension.")
email = EmailValidator(message="Enter a valid email address.")

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# from django.contrib import messages


attachment_max_size = 10.0  # MB
image_types = ["png", "jpg", "jpeg", "tiff", "tif", "bmp"]
attachment_types = ["pdf", "docx", "odt", "txt", "zip"]
file_types = image_types + attachment_types
attachment_valid_type = FileExtensionValidator(file_types)


# on models
def attachment_valid_size(value):
    filesize = value.size
    if filesize > attachment_max_size * 1024 * 1024:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value


# on uploads
def uploaded_attachments_validation(attachment):
    valid_attachments = None
    uploaded_attachments_valid_extensions = file_types

    file_extension = str(attachment.name).split(".")[-1].lower()
    if not attachment.size > attachment_max_size * 1024 * 1024:
        if file_extension in uploaded_attachments_valid_extensions:
            valid_attachments = attachment
            print(f"valid: attachment : {attachment}\t size : {attachment.size}\t ext : {attachment_valid_type}")
        else:
            # raise ValidationError("Invalid Attachment Type!")
            pass
    else:
        # raise ValidationError("Invalid Attachment Size!")
        pass

    return valid_attachments

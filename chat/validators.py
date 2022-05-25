from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# from django.contrib import messages


image_max_size = 10.0  # MB
attachment_max_size = 10.0  # MB
image_types = ["png", "jpg", "jpeg", "tiff", "tif", "bmp", "pdf"]
attachment_types = ["pdf", "docx", "odt", "txt", "zip"]


# on models
def attachment_valid_size(value):
    filesize = value.size
    if filesize > attachment_max_size * 1024 * 1024:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value


def image_valid_size(value):
    filesize = value.size
    if filesize > 7.5 * 1024 * 1024:
        raise ValidationError("The maximum image size that can be uploaded is 7.5MB")
    else:
        return value


attachment_valid_type = FileExtensionValidator(image_types)
image_valid_type = FileExtensionValidator()


# on uploads
def uploaded_attachments_validation(attachments_list=[]):
    valid_attachments = []
    uploaded_attachments_valid_extensions = attachment_types

    for att in attachments_list:
        file_extension = str(att.name).split(".")[-1].lower()
        if not att.size > image_max_size * 1024 * 1024:
            if file_extension in uploaded_attachments_valid_extensions:
                valid_attachments.append(att)
                print(f"valid: attachment : {att}\t size : {att.size}\t ext : {file_extension}")
            else:
                # raise ValidationError("Invalid Attachment Type!")
                pass
        else:
            # raise ValidationError("Invalid Attachment Size!")
            pass

    return valid_attachments


def uploaded_images_validation(images_list=[]):
    valid_images = []
    uploaded_image_valid_extensions = image_types

    for img in images_list:
        image_extension = str(img.name).split(".")[-1].lower()
        if not img.size > 10 * 1024 * 1024:
            if image_extension in uploaded_image_valid_extensions:
                valid_images.append(img)
                print(f"valid: image : {img}\t size : {img.size}\t ext : {image_extension}")
            else:
                # raise ValidationError("Invalid Attachment Type!")
                pass
        else:
            # raise ValidationError("Invalid Attachment Size!")
            pass

    return valid_images

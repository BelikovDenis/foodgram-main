from django.core.exceptions import ValidationError
from PIL import Image


def validate_image_format(image):
    try:
        img = Image.open(image)
        img.verify()
    except (IOError, SyntaxError) as e:
        raise ValidationError('Invalid image format.') from e

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value):
    if not re.match(r'^[\d()+-]+$', value):
        raise ValidationError(_('Invalid phone number format'))
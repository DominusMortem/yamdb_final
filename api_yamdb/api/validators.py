import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_year(value):
    now = datetime.datetime.now()
    if value > now.year:
        raise ValidationError(
            _('%(value)s год ещё не наступил'),
            params={'value': value},
        )
    if value < 0:
        raise ValidationError(
            _('год не может быть отрицательным числом'),
            params={'value': value},
        )

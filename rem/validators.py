from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date


def validate_neg(value):
    if value < 0:
        raise ValidationError(
            _('%(value)s is not a positive number'),
            params={'value': value},
        )

def validate_even(value):
    if value % 2 != 0:
        raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )


def validate_post_date(day):
    if day > date.today():
        raise ValidationError(
            _('%(value)s is a future date'),
            params={'value': day},
        )

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
#from datetime import date
from django.utils import timezone
from django.core.validators import RegexValidator,_lazy_re_compile


western_union = RegexValidator(
    _lazy_re_compile(r'^[0-9]{10}$'),
    message=_('Please enter a valid Western Union MTCN'),
    code='invalid_wu',
)

xpress_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{16}$'),
    message=_('Please enter a valid Xpress Money XPIN'),
    code='invalid_xpress',
)

ria_re = RegexValidator(
    _lazy_re_compile(r'^[0-9a-zA-Z]{8,10}$'),
    message=_('Please enter a valid Ria PIN'),
    code='invalid_ria',
)

placid_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{12}$'),
    message=_('Please enter a valid placid Tracking ID'),
    code='invalid_placid',
)

moneygram_re = RegexValidator(
    _lazy_re_compile(r'^[1-9][0-9]{7}$'),
    message=_('Please enter a valid MoneyGram Reference No.'),
    code='invalid_moneygram',
)

"""swift_re = RegexValidator(
    _lazy_re_compile(r'^^[0-9a-zA-Z]{50}$'),
    message=_('Please enter a valid SWIFT code'),
    code='invalid',
)"""

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
    if day > timezone.localdate():
        raise ValidationError(
            _('%(value)s is a future date'),
            params={'value': day},
        )

def validate_western_code(value):
    return western_union(value)

def validate_alpha_num(value):
    return alpha_num(value)

def validate_xpress(value):
    return xpress_re(value)

def validate_ria(value):
    return ria_re(value)

def validate_placid(value):
    return placid_re(value)

def validate_moneygram(value):
    return moneygram_re(value)

"""def validate_swift(value):
    return swift_re(value)"""

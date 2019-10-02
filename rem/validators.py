from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
#from datetime import date
from django.utils import timezone
from django.core.validators import RegexValidator,_lazy_re_compile
from django.conf import settings
################# models ##############################


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
    _lazy_re_compile(r'^[0-9a-zA-Z]{2}[0-9]{6,10}$'),
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

mobile_re = RegexValidator(
    _lazy_re_compile(r'^(\+8801|8801|01)[3456789][0-9]{8}$'),
    message=_('Please enter a valid Mobile phone number'),
    code='invalid_moneygram',
)

old_nid_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{13,17}$'),
    message=_('Please enter a valid NID number'),
    code='invalid_old_nid',
)

smart_nid_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{10}$'),
    message=_('Please enter a valid NID/ Smart Card number'),
    code='invalid_smart_nid',
)

bc_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{1,17}$'),
    message=_('Please enter a valid Birth Certificate number'),
    code='invalid_bc',
)

passport_re = RegexValidator(
    _lazy_re_compile(r'^[a-zA-Z]{2}[0-9]{7}$'),
    message=_('Please enter a valid passport number'),
    code='invalid_bc',
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


def validate_post_date(datetime):
    if datetime > timezone.now():
        raise ValidationError(
            _('%(value)s is a future date'),
            params={'value': datetime},
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

def validate_mobile(value):
    return mobile_re(value)

"""def validate_swift(value):
    return swift_re(value)"""

def validate_old_nid(value):
    return old_nid_re(value)

def validate_smart_nid(value):
    return smart_nid_re(value)

def validate_bc(value):
    return bc_re(value)

def validate_passport(value):
    return passport_re(value)

def validate_nrbc_mail(email):
    domain = email.split('@')[1]
    if domain!="nrbcommercialbank.com":
        raise ValidationError(
            _('%(email)s is not a valid NRBC email'),
            params={'email': email},
        )

def validate_user_limit(branch):
    total_employee = branch.employee_count(active_status=True)
    if branch.name == 'Head office':
        maximum_allowed_user = settings.MAXIMUM_USER_HEAD_OFFICE
    else:
        maximum_allowed_user = settings.MAXIMUM_USER_PER_BRANCH
    if maximum_allowed_user <= total_employee:
        raise ValidationError(_('Maximum User Limit exceeded for this branch'))

def validate_booth_user_limit(booth):
    total_employee = booth.employee_count(active_status=True)
    maximum_allowed_user = settings.MAXIMUM_USER_PER_BOOTH
    if maximum_allowed_user <= total_employee:
        raise ValidationError(_('Maximum User Limit exceeded for this booth'))

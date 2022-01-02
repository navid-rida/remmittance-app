from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
#from datetime import date
from django.utils import timezone
from django.core.validators import RegexValidator,_lazy_re_compile
from django.conf import settings
################# models ##############################

###################### Regular Expressiosions ################################################

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
    _lazy_re_compile(r'^[0-9]{11}$'),
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

prabhu_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{12}$'),
    message=_('Please enter a valid Prabhu Money Transfer Reference No.'),
    code='invalid_prabhu_ref',
)

merchantrade_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{14}$'),
    message=_('Please enter a valid Merchant Trade Reference No.'),
    code='invalid_merchantrade_ref',
)

necmoney_re = RegexValidator(
    _lazy_re_compile(r'^777[0-9]{12}$'),
    message=_('Please enter a valid NEC Money Transfer Reference No.'),
    code='invalid_necmoney_ref',
)

necitaly_re = RegexValidator(
    _lazy_re_compile(r'^NEC[0-9]{9}$'),
    message=_('Please enter a valid NEC Money Transfer Reference No.'),
    code='invalid_necmoney_ref',
)

cbl_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{9}$'),
    message=_('Please enter a valid CBL Money Transfer Reference No.'),
    code='invalid_cbl_ref',
)


mobile_re = RegexValidator(
    _lazy_re_compile(r'^(\+8801|8801|01)[3456789][0-9]{8}$'),
    message=_('Please enter a valid Mobile phone number'),
    code='invalid_moneygram',
)

old_nid_re = RegexValidator(
    _lazy_re_compile(r'^[0-9]{17}$'),
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

swift_re = RegexValidator(
    _lazy_re_compile(r'^[a-zA-Z]+.{3,50}$'),
    message=_('Please enter a valid SWIFT code'),
    code='invalid',
)

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

def validate_expire_date(date):
    if date < timezone.now().date():
        raise ValidationError(
            _('Document is expired'),
        )

exchange_validators = {
    'WESTERN UNION': western_union,
    'XPRESS MONEY': xpress_re,
    'RIA MONEY TRANSFER': ria_re,
    'PLACID EXPRESS': placid_re,
    'MONEYGRAM': moneygram_re,
    'PRABHU MONEY TRANSFER':prabhu_re,
    'MERCHANTRADE': merchantrade_re,
    'NEC MONEY TRANSFER': necmoney_re,
    'NATIONAL EXCHANGE': necitaly_re,
    'CBL MONEY TRANSFER': cbl_re,
    'SWIFT': swift_re,

}

def validate_all_reference(exchange_name, reference_number, validator_list= exchange_validators):
    validator = validator_list[exchange_name]
    return validator(reference_number)

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

def validate_prabhu_ref(value):
    return prabhu_re(value)

def validate_merchantrade_ref(value):
    year = str(timezone.now().year)
    if year[-2:]!=value[:2]:
        raise ValidationError(
            _('%(year)s is not a valid initial sequence for Merchantrade reference'),
            params={'year': value[:2]},
        )
    return merchantrade_re(value)

def validate_necmoney_ref(value):
    return necmoney_re(value)

def validate_necitaly_ref(value):
    return necitaly_re(value)

def validate_cbl_ref(value):
    return cbl_re(value)


def validate_ref_no(value):
    validator_list=[western_union,placid_re,ria_re,xpress_re,moneygram_re, prabhu_re, merchantrade_re, necmoney_re, necitaly_re, cbl_re]
    for validator in validator_list:
        try:
            validator(value)
            return True
        except ValidationError:
            pass
    raise ValidationError('This is not a valid reference/MTCN')


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

numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')
name = RegexValidator(r'^[a-zA-Z .-]*$', 'Only alphabets are allowed.')
alpha = RegexValidator(r'^[a-zA-Z]*$', 'Only alphabets are allowed.')
alpha_num = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only Alphabet and numeric characters are allowed.')
western_union = RegexValidator(r'^[0-9]{10}$', 'Western union mtcn can contain only 10 digit numbers')
nrbc_acc = RegexValidator(r'^(0|5)[0-9][0-7][0-9][2-3][0-9]{10}$', 'Please provide a valid NRBC account number')

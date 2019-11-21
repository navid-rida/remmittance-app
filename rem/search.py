from .validators import validate_ref_no,validate_mobile
from django.core.exceptions import ValidationError
#from .models import Remmit

def is_ref_no(value):
    try:
        validate_ref_no(value)
    except:
        return False
    return True

def is_mobile_no(keyword):
    try:
        validate_mobile(keyword)
    except:
        return False
    return True

def remittance_search(word,q=None):
    result=q.none()
    if q:
        if is_ref_no(word):
            result = q.filter(reference=word)
        if is_mobile_no(word):
            result = result | q.filter(receiver__cell__contains=word)
        return result
    else:
        return False

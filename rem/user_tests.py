import ipaddress
from .DataModels import get_client_ip
from django.contrib.auth.models import Group

def check_headoffice(user):
    group = Group.objects.get(name='Head office user')
    if group in user.groups.all():
        return True
    else:
        return False

def check_branch(user):
    group = Group.objects.get(name='branch user')
    if group in user.groups.all():
        return True
    else:
        return False

def check_network(request):
    ip = get_client_ip(request)
    ip = ipaddress.ip_address(ip)
    pass

import rules
from rem.DataModels import get_client_ip, get_branch_from_ip

@rules.predicate
def is_remittance_creator(user,remittance):
    return remittance.created_by == user

@rules.predicate
def is_same_branch_user(user,remittance):
    return remittance.branch == user.employee.branch

@rules.predicate
def is_same_branch_user(user,remittance):
    return remittance.branch == user.employee.branch

#is_branch_report_user = rules.is_group_member('branch user')
is_branch_remittance_user = rules.is_group_member('Branch Remittance Info Submission User')
is_branch_report_observer_user = rules.is_group_member('Branch Report Observer User')
is_booth_remittance_user = rules.is_group_member('Booth Remittance Info Submission User')
is_booth_report_observer_user = rules.is_group_member('Booth Report Observer User')
is_ho_settlement_user = rules.is_group_member('HO Settlement User')
is_ho_report_user = rules.is_group_member('HO Report Observer User')

"""@rules.predicate
def is_same_domain_user(user,request):
    ip = get_client_ip(request)
    branch = get_branch_from_ip(ip)
    return branch == user.employee.branch"""


rules.add_perm('rem.change_remmit', is_remittance_creator & is_same_branch_user)
rules.add_perm('rem.add_remmit', is_branch_remittance_user | is_booth_remittance_user)
rules.add_perm('rem.view_branch_remitt', is_branch_report_observer_user)
rules.add_perm('rem.view_booth_remitt', is_booth_report_observer_user)
rules.add_perm('rem.view_all_remitt', is_ho_report_user)
rules.add_perm('rem.view_ho_br_booth_reports', is_ho_report_user)
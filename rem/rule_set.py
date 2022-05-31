import rules
from django.utils import timezone
from datetime import time
from rem.DataModels import get_client_ip, get_branch_from_ip

@rules.predicate
def is_entry_creator(user,entry):
    return entry.created_by == user

@rules.predicate
def is_same_branch_user(user,remittance):
    return remittance.branch == user.employee.branch

@rules.predicate
def is_same_booth_user(user,remittance):
    return remittance.booth == user.employee.booth

@rules.predicate
def is_same_branch_as_creator(user,receiver):
    return receiver.created_by.employee.branch == user.employee.branch

@rules.predicate
def is_ad_branch_user(user, remittance):
    return user.employee.branch.ad_fi_code

@rules.predicate
def is_transaction_hour(user):
    return time(9,29)<timezone.localtime().time()<time(21,00)

@rules.predicate
def remittance_less_than_usd1500(user,remittance):
    return remittance.amount < 150000

@rules.predicate
def remittance_cash_incentive_paid(user,remittance):
    return not remittance.check_unpaid_cash_incentive()

@rules.predicate
def is_thirdparty_exchange_house(user,remittance):
    return remittance.exchange.name != 'SWIFT' and remittance.exchange.name != 'CASH DEPOSIT'


#is_branch_report_user = rules.is_group_member('branch user')
is_branch_remittance_user = rules.is_group_member('Branch Remittance Info Submission User')
is_branch_report_observer_user = rules.is_group_member('Branch Report Observer User')
is_branch_fx_user = rules.is_group_member("Branch SWIFT/Cash deposit remittance update user")
is_booth_remittance_user = rules.is_group_member('Booth Remittance Info Submission User')
is_booth_report_observer_user = rules.is_group_member('Booth Report Observer User')
is_ho_settlement_user = rules.is_group_member('HO Settlement User')
is_ho_report_user = rules.is_group_member('HO Report Observer User')
can_change_benifciary_of_remittance = rules.is_group_member('Change remittance benificiary')


is_api_user = rules.is_group_member('API User')
#is_super = rules.is_superuser(user)

"""@rules.predicate
def is_same_domain_user(user,request):
    ip = get_client_ip(request)
    branch = get_branch_from_ip(ip)
    return branch == user.employee.branch"""


rules.add_perm('rem.change_remmit', is_entry_creator & is_same_branch_user)
rules.add_perm('rem.add_remmit', is_branch_remittance_user | is_booth_remittance_user | (is_branch_fx_user & is_ad_branch_user))
rules.add_perm('rem.add_third_party_remmit', is_branch_remittance_user | is_booth_remittance_user)
rules.add_perm('rem.view_branch_remitt', is_branch_report_observer_user)
rules.add_perm('rem.view_trm_form', ((is_branch_remittance_user & is_same_branch_user)| (is_booth_remittance_user & is_same_booth_user) | is_ho_report_user | rules.is_superuser) & is_thirdparty_exchange_house)
rules.add_perm('rem.view_booth_remitt', is_booth_report_observer_user)
rules.add_perm('rem.view_all_remitt', is_ho_report_user)
rules.add_perm('rem.view_ho_br_booth_reports', is_ho_report_user)
rules.add_perm('rem.can_settle_remitts_cash_incentive', is_ho_settlement_user)
rules.add_perm('rem.can_mark_paid_remittance', rules.is_superuser | is_ho_settlement_user | (is_entry_creator & remittance_less_than_usd1500))
rules.add_perm('rem.can_view_cash_incentive_undertaking', remittance_cash_incentive_paid & is_thirdparty_exchange_house)
rules.add_perm('rem.can_change_benifciary_of_remittance', can_change_benifciary_of_remittance)
#---------------------------------------------------------------------------------

rules.add_perm('rem.change_reciver', is_same_branch_as_creator | rules.is_superuser )
rules.add_perm('rem.allow_if_transaction_hour', is_transaction_hour )

#---------------------------------------------------------------------------------
rules.add_perm('rem.view_claim', (is_entry_creator & is_same_branch_user)| is_ho_report_user | is_ho_report_user)
rules.add_perm('rem.change_claim', is_entry_creator & is_same_branch_user )
rules.add_perm('rem.can_forward_claim', is_ho_settlement_user)

#--------------------------Cash Incentive----------------------------------

rules.add_perm('rem.is_thirdparty_remittance', is_thirdparty_exchange_house)
#----------------------- API --------------------

rules.add_perm('remapi.is_api_user', is_api_user)

#-------------------------- Encachment------------------------------------
rules.add_perm('rem.can_encash', ~is_thirdparty_exchange_house)

#-------------------------- SWIFt and Cash deposrit------------------------------------

rules.add_perm('rem.can_add_swift_cash_deposit_remit', is_branch_fx_user & is_ad_branch_user)

#-------------------------- Branch Operations------------------------------------
rules.add_perm('rem.can_view_branch_options', is_branch_remittance_user | is_booth_remittance_user | (is_branch_fx_user & is_ad_branch_user))

#-------------------------- HO Operations------------------------------------
rules.add_perm('rem.can_view_ho_options',is_ho_report_user | is_ho_settlement_user)
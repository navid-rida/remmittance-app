from rem.models import Encashment, Remmit, CashIncentive, Encashment
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils import timezone
#from django.contrib import messages


@receiver(post_save, sender= Remmit)
def create_cash_incentive(sender, instance, created, **kwargs):
    if created:
        if instance.is_thirdparty_remittance():
            if instance._entry_cat=='P':
                CashIncentive.objects.create(remittance = instance, cash_incentive_amount= instance.calculate_cash_incentive(), date_cash_incentive_paid=timezone.now(), entry_category=instance._entry_cat )
            elif (instance._entry_cat == 'U' or instance._entry_cat == 'NA'):
                CashIncentive.objects.create(remittance = instance, cash_incentive_amount= 0, entry_category=instance._entry_cat, unpaid_cash_incentive_reason=instance._reason_a)
            else:
                pass
        else:
            pass
    else:
        if instance.is_thirdparty_remittance() and hasattr(instance, '_entry_cat'):
            if instance.cashincentive_set.all().exists():
                ci = instance.cashincentive_set.all().last()
                if instance._entry_cat=='P':
                    ci.cash_incentive_amount= instance.calculate_cash_incentive()
                    ci.date_cash_incentive_paid=timezone.now()
                    ci.entry_category=instance._entry_cat
                    ci.save()
                elif (instance._entry_cat == 'U' or instance._entry_cat == 'NA'):
                    ci.cash_incentive_amount= 0
                    ci.date_cash_incentive_paid=None
                    ci.entry_category=instance._entry_cat
                    ci.unpaid_cash_incentive_reason=instance._reason_a
                    ci.save()
                else:
                    pass
            else:
                if instance.is_thirdparty_remittance():
                    if instance._entry_cat=='P':
                        CashIncentive.objects.create(remittance = instance, cash_incentive_amount= instance.calculate_cash_incentive(), date_cash_incentive_paid=timezone.now(), entry_category=instance._entry_cat )
                    elif (instance._entry_cat == 'U' or instance._entry_cat == 'NA'):
                        CashIncentive.objects.create(remittance = instance, cash_incentive_amount= 0, entry_category=instance._entry_cat, unpaid_cash_incentive_reason=instance._reason_a)
                    else:
                        pass
        else:
            pass


        """else:
            pass
        if instance._entry_cat=='P' and instance.is_thirdparty_remittance():
            if not instance.cashincentive_set.filter(entry_category='P').exists():
                CashIncentive.objects.create(remittance = instance, cash_incentive_amount= instance.calculate_cash_incentive(), date_cash_incentive_paid=timezone.now(), entry_category=instance.cash_incentive_status )
            else:
                if instance.cashincentive_set.filter(entry_category='P').count()>1:
                    pass #messages.info('It seems that the remittance has more than one cash incentive. Please contact admin')
                else:
                    ci = instance.cashincentive_set.get(entry_category='P')
                    ci.cash_incentive_amount= instance.calculate_cash_incentive()
                    ci.date_cash_incentive_paid=timezone.now()
                    ci.entry_category=instance._entry_cat
                    ci.save()
                    #messages.success('S Message')"""


    """else:
        #This section should be removed after implementing seperate Cash Incentive Table
        if instance._entry_cat and instance._entry_cat=='P' and (not instance.check_if_cash_incentive_paid()):
            CashIncentive.objects.create(remittance = instance, cash_incentive_amount= instance.calculate_cash_incentive(), date_cash_incentive_paid=timezone.now(), entry_category=instance._entry_cat )"""
        

@receiver(post_save, sender= Encashment)
def create_encashment(sender, instance, created, **kwargs):
    if created:
        if instance.cashin_category=='P':
            CashIncentive.objects.create(remittance = instance.remittance, encashment=instance, cash_incentive_amount= instance.calculate_cash_incentive(), date_cash_incentive_paid=timezone.now(), entry_category=instance.cashin_category )
        else:
            CashIncentive.objects.create(remittance = instance.remittance, encashment=instance, cash_incentive_amount= 0, entry_category=instance.cashin_category, unpaid_cash_incentive_reason=instance.reason)
    
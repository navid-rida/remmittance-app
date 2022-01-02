from rem.models import Encashment, Remmit, CashIncentive, Encashment
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils import timezone


@receiver(post_save, sender= Remmit)
def create_cash_incentive(sender, instance, created, **kwargs):
    if created:
        if instance._entry_cat=='P':
            CashIncentive.objects.create(remittance = instance, cash_incentive_amount= instance.calculate_cash_incentive(), date_cash_incentive_paid=timezone.now(), entry_category=instance._entry_cat )
        elif instance._entry_cat == 'U':
            CashIncentive.objects.create(remittance = instance, cash_incentive_amount= 0, entry_category=instance._entry_cat, unpaid_cash_incentive_reason=instance._reason_a)
        else:
            pass
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
    
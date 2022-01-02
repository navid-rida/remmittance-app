from django.contrib import admin
from .models import Remmit, Branch,ExchangeHouse, Employee, Country, Receiver, Requestpay,Payment, Booth,Claim, CashIncentive,  Encashment, Account
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Permission
# Register your models here.
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'employee'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline, )

class RemmitAdmin(admin.ModelAdmin):
    search_fields = ('reference',)
class PaymentAdmin(admin.ModelAdmin):
    search_fields = ('requestpay__remittance__reference',)

class RequestpayAdmin(admin.ModelAdmin):
    search_fields = ('remittance__reference',)

class ReceiverAdmin(admin.ModelAdmin):
    search_fields = ('idno','name','cell')

class CashIncentiveAdmin(admin.ModelAdmin):
    search_fields = ('remittance__reference',)

class RemittanceUpdateHistoryAdmin(admin.ModelAdmin):
    search_fields = ('remittance__reference',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Permission)
admin.site.register(Remmit, RemmitAdmin)
admin.site.register(Branch)
admin.site.register(ExchangeHouse)
admin.site.register(Employee)
admin.site.register(Country)
admin.site.register(Receiver,ReceiverAdmin)
admin.site.register(Requestpay, RequestpayAdmin)
admin.site.register(Payment, PaymentAdmin)
#admin.site.register(ReceiverUpdateHistory)
#admin.site.register(RemittanceUpdateHistory)
admin.site.register(Booth)
admin.site.register(Claim)
admin.site.register(CashIncentive, CashIncentiveAdmin)
#admin.site.register(RemittanceUpdateHistory, RemittanceUpdateHistoryAdmin)
admin.site.register(Encashment)
admin.site.register(Account)

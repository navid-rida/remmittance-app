from django.contrib import admin
from .models import Remmit, Branch,ExchangeHouse, Employee, Country, Receiver, Requestpay,Payment,ReceiverUpdateHistory
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'employee'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Remmit)
admin.site.register(Branch)
admin.site.register(ExchangeHouse)
admin.site.register(Employee)
admin.site.register(Country)
admin.site.register(Receiver)
admin.site.register(Requestpay)
admin.site.register(Payment)
admin.site.register(ReceiverUpdateHistory)

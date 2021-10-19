from django.contrib import admin
from .models import Currency,District,Bank, Rate



class CurrencyAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# Register your models here.

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(District)
admin.site.register(Bank)
admin.site.register(Rate)

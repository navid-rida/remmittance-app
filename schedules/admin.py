from django.contrib import admin
from .models import Currency,District,Bank, Rate

# Register your models here.

admin.site.register(Currency)
admin.site.register(District)
admin.site.register(Bank)
admin.site.register(Rate)

from .models import Remmit, ExchangeHouse, Branch
from django.forms import ModelForm
from django import forms
#from datetime import date
from django.utils import timezone
#from django.contrib.admin.widgets import AdminDateWidget

class RemmitForm(ModelForm):

    class Meta:
        model = Remmit
        fields = ('exchange','rem_country','reference','sender','reciever','amount','mode','date',)
        widgets = {
            'date': forms.SelectDateWidget,
        }

class CsvForm(forms.Form):
    date = forms.DateField(label="Date for download", initial=timezone.now, widget=forms.SelectDateWidget)

class SearchForm(forms.Form):
    date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False)
    date_to = forms.DateField(label="Ending Date", initial=timezone.now, required=False)
    exchange = forms.ModelChoiceField(queryset=ExchangeHouse.objects.all(),required=False)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),required=False)

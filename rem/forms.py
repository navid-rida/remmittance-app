from .models import Remmit
from django.forms import ModelForm
from django import forms
from datetime import date
#from django.contrib.admin.widgets import AdminDateWidget

class RemmitForm(ModelForm):

    class Meta:
        model = Remmit
        fields = ('branch','exchange','rem_country','reference','sender','reciever','amount','mode','date',)
        widgets = {
            'date': forms.SelectDateWidget,
        }

class CsvForm(forms.Form):
    date = forms.DateField(label="Date for download", initial=date.today(), widget=forms.SelectDateWidget)

class SearchForm(forms.Form):
    date_from = forms.DateField(label="Starting Date", initial=date.today(),widget=forms.SelectDateWidget)
    date_to = forms.DateField(label="Ending Date", initial=date.today(),widget=forms.SelectDateWidget)

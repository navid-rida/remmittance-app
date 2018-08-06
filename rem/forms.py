from .models import Remmit
from django.forms import ModelForm
from django import forms
from datetime import date
#from django.contrib.admin.widgets import AdminDateWidget

class RemmitForm(ModelForm):

    """def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].widget.attrs.update({'class': 'form-control'})
        self.fields['exchange'].widget.attrs.update({'class': 'form-control'})
        self.fields['rem_country'].widget.attrs.update({'class': 'form-control'})
        self.fields['sender'].widget.attrs.update({'class': 'form-control'})
        self.fields['reciever'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        #self.fields['comment'].widget.attrs.update(size='40')"""

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

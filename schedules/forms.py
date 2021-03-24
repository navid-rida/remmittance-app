from .models import Rate
from django.forms import ModelForm
from django import forms

#############Crispy Forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit #, Fieldset, ButtonHolder, Submit


class RateForm(ModelForm):
    date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])

    class Meta:
        model = Rate
        fields = ['currency', 'rate_type','date', 'rate']

    def __init__(self, *args, **kwargs):
        super(RateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.render_unmentioned_fields= True
        self.helper.layout = Layout(
            'currency',
            'rate_type',
            'rate',
            Field('date', css_class="date"),
            Submit('submit', 'CREATE'),
        )    
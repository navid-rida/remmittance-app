from django.shortcuts import render
from .forms import RateForm
from .models import Rate
from django.contrib.auth.decorators import login_required #,user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView,UpdateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy,reverse
###Rules
from rules.contrib.views import PermissionRequiredMixin, permission_required, objectgetter

# Create your views here.

@method_decorator([login_required], name='dispatch')
class RateCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Rate
    form_class = RateForm
    permission_required = ['rem.allow_if_transaction_hour']
    template_name = 'schedules/forms/rate_create_form.html'
    success_message = "Rate successfully inserted"
    success_url = reverse_lazy('index')

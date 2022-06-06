from django.shortcuts import render
from .forms import RateForm
from rem.forms import SearchForm
from .models import Rate
from .DataModels import *
from rem.DataModels import *
from django.contrib.auth.decorators import login_required #,user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView,UpdateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
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

@login_required
@permission_required('rem.view_ho_br_booth_reports')
def remittance_rit_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        #filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            query_set = CashIncentive.objects.filter(entry_category='P', date_cash_incentive_settlement__isnull=False)
            if date_from and date_to:
                query_set = query_set.filter(date_cash_incentive_settlement__range=(date_from,date_to))
            #q = filter_remittance(query_set,start_date=date_from, end_date= date_to)
            #q = filter_remittance(query_set, start_date=date_from, end_date= date_to, cash_incentive_status='P', cash_incentive_settlement_done=True)
            #q = query_set.filter(dateresolved__date__range=(date_from,date_to))
            statement = cash_incentive_rit(qset=query_set)
            if '_show' in request.POST:
                context = {'form':form, 'df': statement.to_html(classes = "table table-hover table-sm"), 'q':query_set}
                return render(request, 'schedules/reports/rit.html', context)
            if '_download' in request.POST:
                #df = pd.DataFrame(summary_list, columns=['code','name','count','sum'])
                xlsx_data = excel_output(statement)
                response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                time = str(timezone.now().date())
                filename = "RIT"+time+".xlsx"
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                #writer.save(re)
                return response
        else:
            context = {'form':form }
            return render(request, 'schedules/reports/rit.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        return render(request, 'schedules/reports/rit.html', context)

@login_required
@permission_required('rem.view_ho_br_booth_reports')
def currency_rate_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        #filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            query_set = Rate.objects.all()
            if date_from and date_to:
                query_set = query_set.filter(date__range=(date_from,date_to))
            #q = filter_remittance(query_set,start_date=date_from, end_date= date_to)
            #q = filter_remittance(query_set, start_date=date_from, end_date= date_to, cash_incentive_status='P', cash_incentive_settlement_done=True)
            #q = query_set.filter(dateresolved__date__range=(date_from,date_to))
            #df = qset_to_df(query_set)
            if '_show' in request.POST:
                context = {'form':form, 'q':query_set}
                return render(request, 'schedules/reports/rates/rate_list.html', context)
            if '_download' in request.POST:
                #df = pd.DataFrame(summary_list, columns=['code','name','count','sum'])
                xlsx_data = excel_output(qset_to_df(query_set))
                response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                time = str(timezone.now().date())
                filename = "Rate List "+time+".xlsx"
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                #writer.save(re)
                return response
        else:
            context = {'form':form }
            return render(request, 'schedules/reports/rates/rate_list.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        return render(request, 'schedules/reports/rates/rate_list.html', context)
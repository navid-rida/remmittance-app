from django.shortcuts import render,redirect#, render_to_response
from django.http import HttpResponse
from .forms import RemmitForm, CsvForm, SearchForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Remmit
import datetime
from .DataModels import *
import io
from django.contrib import messages
from django.views.generic.edit import CreateView,UpdateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.utils import timezone
# Create your views here.

###############User tests############################
def check_headoffice(user):
    group = Group.objects.get(name='Head office user')
    if group in user.groups.all():
        return True
    else:
        return False


@method_decorator(login_required, name='dispatch')
class RemmitCreate(CreateView):
    model = Remmit
    form_class = RemmitForm
    template_name = 'rem/forms/remmit_create_form.html'
    success_url = reverse_lazy('remmit-create')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.branch = self.request.user.employee.branch
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class RemmitUpdate(UpdateView):
    model = Remmit
    form_class = RemmitForm
    template_name = 'rem/forms/remmit_update_form.html'
    success_url = reverse_lazy('show_rem')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

@login_required
def index(request):
    latest_question_list = 0
    context = {'latest_question_list': latest_question_list}
    return render(request, 'rem/base.html', context)

@login_required
def show_rem(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            exchange = form.cleaned_data['exchange']
            if check_headoffice(request.user):
                rem_list = search(date_from=date_from,date_to=date_to,exchange=exchange)
            else:
                rem_list = search(date_from=date_from,date_to=date_to,exchange=exchange, branch=request.user.employee.branch)
            context = {'rem_list': rem_list, 'form':form, 'date': date_from}
            return render(request, 'rem/report/rem_list.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/rem_list.html', context)

@login_required
@user_passes_test(check_headoffice)
def select_rem_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            #date_from = form.cleaned_data['date_from']
            #date_to = form.cleaned_data['date_to']
            exchange = form.cleaned_data['exchange']
            branch = form.cleaned_data['branch']
            rem_list = search(branch=branch,exchange=exchange,status='NS')
            if rem_list:
                df = qset_to_df(rem_list)
                ids = list(df['id'][df.duplicated(['amount','branch_id','exchange_id'],keep=False)==True].values)
                context = {'rem_list': rem_list, 'form':form, 'ids':ids}
            else:
                context = {'form':form}
        else:
            context = {'form':form}
    else:
        form = SearchForm()
        context = {'form':form}

    return render(request, 'rem/report/download_excel.html', context)

@login_required
@user_passes_test(check_headoffice)
def mark_rem_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            exchange = form.cleaned_data['exchange']
            branch = form.cleaned_data['branch']
            rem_list = search(status='NS',date_from=date_from,date_to=date_to,exchange=exchange)
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/mark_settle.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/mark_settle.html', context)


@login_required
@user_passes_test(check_headoffice)
def download_bb_excel(request):
    date = "no date "
    if request.method == 'POST': # If the form has been submitted...
        form = CsvForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...

            date = form.cleaned_data['date']
            df = rem_bb_summary(date)
            xlsx_data = excel_output(df)
            response = HttpResponse(xlsx_data,content_type='application/vnd.ms-excel')
            time = str(tomezone.now)
            #filename = "output "+time+".xls"
            response['Content-Disposition'] = 'attachment; filename="somefilename.xls"'
            #writer.save(re)
            return response

            #return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = CsvForm() # An unbound form

    return render(request, 'rem/forms/csv_download.html', {
        'form': form,
        'date' : date,
    })

@login_required
@user_passes_test(check_headoffice)
def download_selected_excel(request):

    if request.method == 'POST' and request.POST.getlist('checks'):
        list = request.POST.getlist('checks') # If the form has been submitted...
        #form = Remmit.objects.filter(id__in=selected_values)
        df = rem_bb_summary(list)
        xlsx_data = excel_output(df)
        response = HttpResponse(xlsx_data,content_type='application/vnd.ms-excel')
        time = str(timezone.now)
        #filename = "output "+time+".xls"
        response['Content-Disposition'] = 'attachment; filename="somefilename.xls"'
        #writer.save(re)
        return response
    else:
        form = SearchForm()
        list = "Please select at least one entry " # An unbound form

    return redirect('select_rem_list')

@login_required
@user_passes_test(check_headoffice)
def mark_settle(request):
    if request.method == 'POST':
        list = request.POST.getlist('checks') # If the form has been submitted...
        #form = Remmit.objects.filter(id__in=selected_values)
        for id in list:
            entry = Remmit.objects.get(pk=id)
            entry.status = 'ST'
            entry.save()
    return redirect('mark_rem_list')

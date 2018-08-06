from django.shortcuts import render,redirect#, render_to_response
from django.http import HttpResponse
from .forms import RemmitForm, CsvForm, SearchForm
#from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Remmit
from datetime import date
from .DataModels import *
import io
from django.contrib import messages
from django.views.generic.edit import CreateView,UpdateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
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
    #fields = ['name']
    template_name = 'rem/forms/remmit_create_form.html'
    success_url = reverse_lazy('remmit-create')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if self.request.user.employee.branch.code != '0100':
            form.instance.branch = self.request.user.employee.branch
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class RemmitUpdate(UpdateView):
    model = Remmit
    form_class = RemmitForm
    #fields = ['name']
    template_name = 'rem/forms/remmit_update_form.html'
    success_url = '/'

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
            rem_list = Remmit.objects.filter(date__range=[date_from, date_to]).filter(branch=request.user.employee.branch).order_by('exchange', '-date')
            context = {'rem_list': rem_list, 'form':form}
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
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            rem_list = Remmit.objects.filter(date__range=[date_from, date_to]).filter(status='NS').order_by('exchange', '-date')
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/download_excel.html', context)
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
            rem_list = Remmit.objects.filter(date__range=[date_from, date_to]).order_by('exchange', '-date')
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/mark_settle.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/mark_settle.html', context)



"""@login_required
def show_rem(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            rem_list = Remmit.objects.filter(date__range=[date_from, date_to]).order_by('exchange', '-date')
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/new_rem_list.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/new_rem_list.html', context)"""


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
            time = str(date.today())
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

    if request.method == 'POST':
        list = request.POST.getlist('checks') # If the form has been submitted...
        #form = Remmit.objects.filter(id__in=selected_values)
        df = rem_bb_summary(list)
        xlsx_data = excel_output(df)
        response = HttpResponse(xlsx_data,content_type='application/vnd.ms-excel')
        time = str(date.today())
        #filename = "output "+time+".xls"
        response['Content-Disposition'] = 'attachment; filename="somefilename.xls"'
        #writer.save(re)
        return response
    else:
        list = "no list " # An unbound form

    return render(request, 'rem/report/ex_test.html', {
        'list': list,

    })

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

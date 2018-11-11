from django.shortcuts import render,redirect, get_object_or_404#, render_to_response
from django.http import HttpResponse
from .forms import RemmitForm, SearchForm, ReceiverSearchForm, ReceiverForm, PaymentForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Remmit, Requestpay, Receiver
import datetime
from .DataModels import *
import io
from django.contrib import messages
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy,reverse
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db import transaction
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.

###############User tests############################
def check_headoffice(user):
    group = Group.objects.get(name='Head office user')
    if group in user.groups.all():
        return True
    else:
        return False

def check_branch(user):
    group = Group.objects.get(name='branch user')
    if group in user.groups.all():
        return True
    else:
        return False

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitCreate(SuccessMessageMixin, CreateView):
    model = Remmit
    form_class = RemmitForm
    template_name = 'rem/forms/remmit_create_form.html'
    success_message = "Remittance request was submitted successfully"
    #pk = self.kwargs['pk']
    #rcvr = Receiver.objects.get(pk=pk)
    success_url = reverse_lazy('index')

    """def get_success_url(self):
        return reverse('add_req', kwargs={'pk': self.object.id})"""

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.branch = self.request.user.employee.branch
        receiver = get_object_or_404(Receiver, pk=self.kwargs['pk'])
        form.instance.receiver = receiver
        self.object = form.save(commit=False)
        # in case you want to modify the object before commit
        self.object.save()
        req = Requestpay(remittance=self.object, created_by=self.request.user)
        req.save()
        return super().form_valid(form)

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitUpdate(UpdateView):
    model = Remmit
    form_class = RemmitForm
    template_name = 'rem/forms/remmit_update_form.html'
    success_url = reverse_lazy('show_rem')

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
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
            context = {'form':form, 'valid':'Not valid'}

    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/rem_list.html', context)

@login_required
def show_req(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            if (date_from != None) and (date_to!= None):
                filt['datecreate__date__range'] = (date_from,date_to)
            else:
                filt['datecreate__date__range'] = None
            filt['remittance__exchange'] = form.cleaned_data['exchange']
            filt['status'] = form.cleaned_data['status']
            filt['remittance__branch'] = form.cleaned_data['branch']
            filt['resubmit_flag'] = False
            if check_headoffice(request.user):
                filter_args = {k:v for k,v in filt.items() if v is not None}
                req_list = Requestpay.objects.filter(**filter_args)
                context = {'req_list': req_list, 'form':form}
                return render(request, 'rem/report/req_list_ho.html', context)
            else:
                filt['remittance__branch'] = request.user.employee.branch
                filter_args = {k:v for k,v in filt.items() if v is not None}
                req_list = Requestpay.objects.filter(**filter_args)
                context = {'req_list': req_list, 'form':form}
                return render(request, 'rem/report/req_list_branch.html', context)
        else:
            context = {'form':form }
            if check_headoffice(request.user):
                return render(request, 'rem/report/req_list_ho.html', context)
            else:
                return render(request, 'rem/report/req_list_branch.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        if check_headoffice(request.user):
            return render(request, 'rem/report/req_list_ho.html', context)
        else:
            return render(request, 'rem/report/req_list_branch.html', context)

@login_required
@user_passes_test(check_headoffice)
def select_rem_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        filt = {}
        if form.is_valid():
            #date_from = form.cleaned_data['date_from']
            #date_to = form.cleaned_data['date_to']
            filt['requestpay__remittance__exchange'] = form.cleaned_data['exchange']
            filt['requestpay__remittance__branch'] = form.cleaned_data['branch']
            filt['status'] = 'U'
            filter_args = {k:v for k,v in filt.items() if v is not None}
            rem_list = Payment.objects.filter(**filter_args)
            if rem_list:
                df = qset_to_df(rem_list)
                #ids = list(df['id'][df.duplicated(['amount','branch_id','exchange_id'],keep=False)==True].values)
                context = {'rem_list': rem_list, 'form':form}
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
        filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            if (date_from != None) and (date_to!= None):
                filt['dateresolved__date__range'] = (date_from,date_to)
            else:
                filt['dateresolved__date__range'] = None
            filt['requestpay__remittance__exchange'] = form.cleaned_data['exchange']
            filt['requestpay_remittance__branch']  = form.cleaned_data['branch']
            filt['status']  = 'U'
            filter_args = {k:v for k,v in filt.items() if v is not None}
            rem_list = Payment.objects.filter(**filter_args)
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/mark_settle.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/mark_settle.html', context)

@login_required
#@user_passes_test(check_headoffice)
def search_receiver(request):
    if request.method == "POST":
        form = ReceiverSearchForm(request.POST)
        if form.is_valid():
            identification = form.cleaned_data['identification']
            try:
                receiver = Receiver.objects.get(idno=identification)
                #messages.info(request, '')
                context = {'receiver': receiver, 'msg':'Entry Found', 'form': form}
            except Receiver.DoesNotExist:
                form = ReceiverForm()
                context = {'form': form, 'msg':'Entry  Not Found'}
                return redirect('add_client')
        else:
            context = {'form':form}
    else:
        form = ReceiverSearchForm()
        context = {'form':form, 'msg':'Enter a phone number to search existing customer'}
    return render(request, 'rem/process/receive_search.html', context)


@method_decorator([login_required,transaction.atomic],name='dispatch')
class ReceiverCreate(SuccessMessageMixin, CreateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = 'rem/forms/receiver_create_form.html'
    success_message = "Customer was created successfully"
    #success_url = reverse_lazy('remmit-create',args=(self.object.id,))

    def get_success_url(self):
        return reverse('remmit-create', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    """def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReceiverCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['rform'] = context['form']
        context['form'] = ReceiverSearchForm()
        return context"""

@method_decorator([login_required,transaction.atomic],name='dispatch')
class ReceiverUpdate(UpdateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = 'rem/forms/receiver_create_form.html'
    #success_url = reverse_lazy('remmit-create',args=(self.object.id,))

    def get_success_url(self):
        return reverse('remmit-create', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    """def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReceiverCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['rform'] = context['form']
        context['form'] = ReceiverSearchForm()
        return context"""

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
@transaction.atomic
def mark_settle(request):
    if request.method == 'POST':
        list = request.POST.getlist('checks') # If the form has been submitted...
        #form = Remmit.objects.filter(id__in=selected_values)
        for id in list:
            entry = Payment.objects.get(pk=id)
            entry.status = 'S'
            entry.save()
    return redirect('mark_rem_list')

@login_required
def RequestPayCreate(request):
    if request.method == 'POST':
        pass
    else:
        pk = pk=self.kwargs['pk']
        remitt = Remmit.objects.get(pk=pk)
        context = {}
    return redirect('mark_rem_list')

############################# Details Views#################################
@method_decorator([login_required,], name='dispatch')
class RequestpayDetailView(DetailView):
    model = Requestpay
    template_name = 'rem/detail/requestpay_detail_base.html'

    """def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PaymentForm()
        return context"""

@login_required
@user_passes_test(check_headoffice)
@transaction.atomic
def payment_confirm(request, pk):
    #pk = pk
    req = Requestpay.objects.get(pk=pk)
    payment_entry = hasattr(req, 'payment')
    if payment_entry or (req.resubmit_flag==True):
        messages.warning(request, 'This request is either already paid or resubmitted')
        return redirect('requestpay-detail',pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            confirmation = form.cleaned_data['confirmation']
            comment = form.cleaned_data['comment']
            if confirmation == 'P':
                payment = Payment()
                payment.requestpay = req
                payment.paid_by = request.user
                payment.screenshot = request.FILES.get('screenshot',False) #REVIEW NEEDED"""
                payment.save()
                req.status = 'PD'
                req.save()
                messages.success(request, 'Payment done')
                return redirect('show_req')
            else:
                req.status = 'RJ'
                req.save()
                messages.info(request, 'Request Rejected')
                return redirect('show_req')
        else:
            context={'form':form, 'object':req}
            return render(request, 'rem/detail/requestpay_paymentaction.html', context)
    else:
        form = PaymentForm()
        context = context={'form':form, 'object':req}
        return render(request, 'rem/detail/requestpay_paymentaction.html', context)

@login_required
@user_passes_test(check_branch)
@transaction.atomic
def request_resubmit(request, pk):
    req = Requestpay.objects.get(pk=pk)
    remit = req.remittance
    client = req.remittance.receiver
    if req.resubmit_flag==True:
        messages.warning(request, 'This request has already been resubmitted')
        return redirect('requestpay-detail',pk)
    if request.method == 'POST':
        rem_form = RemmitForm(request.POST, instance=remit)
        receiver_form = ReceiverForm(request.POST, instance=client)
        if rem_form.is_valid() and receiver_form.is_valid():
            remitt = rem_form.save()
            receiver_form.save()
            new_req = Requestpay()
            new_req.remittance = remitt
            new_req.created_by = request.user
            new_req.save()
            req.resubmit_flag=True
            req.save()
            return redirect('show_req')
        else:
            context = {'form': receiver_form, 'rform': rem_form}
    else:
        rem_form = RemmitForm(instance=remit)
        receiver_form = ReceiverForm(instance=client)
        context = {'form': receiver_form, 'rform': rem_form}
    return render(request,'rem/forms/remmit_resubmit.html',context)

from django.shortcuts import render,redirect, get_object_or_404#, render_to_response
from django.http import HttpResponse
from .forms import RemmitForm, SearchForm, ReceiverSearchForm, ReceiverForm, PaymentForm, SignUpForm, RemittInfoForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Remmit, Requestpay, Receiver,Employee, ReceiverUpdateHistory
import datetime
from .DataModels import *
from .user_tests import *
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
from django.conf import settings
from django.core.exceptions import ValidationError
############################### djang-registration imports ##########################
from django_registration.backends.activation.views import RegistrationView
from django_registration import signals
# Create your views here.

MAXIMUM_AllOWWED_USER_PER_BRANCH = settings.MAXIMUM_USER_PER_BRANCH

###############User tests############################
"""def check_user_available(branch, MAXIMUM_AllOWWED_USER_PER_BRANCH):
    number = branch.employee_set.all().count()
    if number >= MAXIMUM_AllOWWED_USER_PER_BRANCH:
        return False
    else:
        return True"""

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitCreate(SuccessMessageMixin, CreateView):
    model = Remmit
    form_class = RemmitForm
    template_name = 'rem/forms/remmit_create_form.html'
    success_message = "Remittance request was submitted successfully"
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
        req = Requestpay(remittance=self.object, created_by=self.request.user, ip=get_client_ip(self.request))
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
        filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            if (date_from != None) and (date_to!= None):
                filt['datecreate__date__range'] = (date_from,date_to)
            else:
                filt['datecreate__date__range'] = None
            filt['remittance__exchange'] = form.cleaned_data['exchange']
            filt['status'] = 'PD'
            filt['remittance__branch'] = form.cleaned_data['branch']
            filt['resubmit_flag'] = False
            if check_headoffice(request.user):
                filter_args = {k:v for k,v in filt.items() if v is not None}
                req_list = Requestpay.objects.filter(**filter_args).order_by('remittance__exchange','-datecreate')
                context = {'pay_list': req_list, 'form':form}
                return render(request, 'rem/report/payment_list_ho.html', context)
            else:
                filt['remittance__branch'] = request.user.employee.branch
                filter_args = {k:v for k,v in filt.items() if v is not None}
                req_list = Requestpay.objects.filter(**filter_args).order_by('remittance__exchange','-datecreate')
                context = {'pay_list': req_list, 'form':form}
                return render(request, 'rem/report/payment_list_branch.html', context)
        else:
            context = {'form':form }
            if check_headoffice(request.user):
                return render(request, 'rem/report/payment_list_ho.html', context)
            else:
                return render(request, 'rem/report/payment_list_branch.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        if check_headoffice(request.user):
            return render(request, 'rem/report/payment_list_ho.html', context)
        else:
            return render(request, 'rem/report/payment_list_branch.html', context)

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
            status = form.cleaned_data['status']
            if status == 'AL':
                filt['status'] = None
            else:
                filt['status'] = status
            filt['remittance__branch'] = form.cleaned_data['branch']
            filt['resubmit_flag'] = False
            if check_headoffice(request.user):
                filter_args = {k:v for k,v in filt.items() if v is not None}
                req_list = Requestpay.objects.filter(**filter_args).order_by('remittance__exchange','-datecreate')
                context = {'req_list': req_list, 'form':form}
                return render(request, 'rem/report/req_list_ho.html', context)
            else:
                filt['remittance__branch'] = request.user.employee.branch
                filter_args = {k:v for k,v in filt.items() if v is not None}
                req_list = Requestpay.objects.filter(**filter_args).order_by('remittance__exchange','-datecreate')
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
            rem_list = Payment.objects.filter(**filter_args).order_by('requestpay__remittance__exchange','-dateresolved')
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
            filt['requestpay__remittance__branch']  = form.cleaned_data['branch']
            filt['status']  = 'U'
            filter_args = {k:v for k,v in filt.items() if v is not None}
            rem_list = Payment.objects.filter(**filter_args).order_by('requestpay__remittance__exchange','-dateresolved')
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/mark_settle.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/mark_settle.html', context)

@login_required
@user_passes_test(check_branch)
#@user_passes_test(check_headoffice)
def search_receiver(request):
    if request.method == "POST":
        form = ReceiverSearchForm(request.POST)
        if form.is_valid():
            identification = form.cleaned_data['identification']
            try:
                receiver = Receiver.objects.get(idno=identification)
                context = {'receiver': receiver, 'form': form}
            except Receiver.DoesNotExist:
                form = ReceiverForm()
                messages.info(request, 'No customer was found with this identification, Please add a new receiver')
                context = {'form': form}
                return redirect('add_client')
        else:
            context = {'form':form}
    else:
        form = ReceiverSearchForm()
        context = {'form':form}
    return render(request, 'rem/process/receive_search.html', context)


@method_decorator([login_required,transaction.atomic],name='dispatch')
class ReceiverCreate(SuccessMessageMixin, CreateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = 'rem/forms/receiver_create_form.html'
    success_message = "Customer was created successfully"
    #success_url = reverse_lazy('remmit-create',args=(self.object.id,))

    def get_success_url(self):
        #return reverse('remmit-create', kwargs={'pk': self.object.id})
        return reverse('remmit-create-with-payment', kwargs={'pk': self.object.id})

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
    template_name = 'rem/forms/receiver_edit_form.html'
    #success_url = reverse_lazy('remmit-create',args=(self.object.id,))

    def get_success_url(self):
        return reverse('remmit-create-with-payment', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        update = ReceiverUpdateHistory()
        update.receiver= self.object
        update.createdby = self.request.user
        update.ip = get_client_ip(self.request)
        update.save()
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
            response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            time = str(tomezone.now)
            #filename = "output "+time+".xls"
            response['Content-Disposition'] = 'attachment; filename="somefilename.xlsx"'
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
        response = HttpResponse(xlsx_data,content_type='pplication/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        time = str(timezone.now)
        #filename = "output "+time+".xls"
        response['Content-Disposition'] = 'attachment; filename="somefilename.xlsx"'
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
@user_passes_test(check_branch)
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
                payment.ip = get_client_ip(request)
                payment.agent_screenshot = request.FILES.get('agent_screenshot',False) # REVIEW NEEDED
                payment.customer_screenshot = request.FILES.get('customer_screenshot',False) # REVIEW NEEDED
                payment.western_trm_screenshot = request.FILES.get('western_trm_screenshot',False) # REVIEW NEEDED
                payment.save()
                req.status = 'PD'
                req.save()
                messages.success(request, 'Payment done')
                return redirect('show_req')
            else:
                req.status = 'RJ'
                req.comment = comment
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
    if req.resubmit_flag==True or req.status != 'RJ':
        messages.warning(request, 'This request has already been resubmitted or has not been rejected')
        return redirect('requestpay-detail',pk)
    remit = req.remittance
    client = req.remittance.receiver
    if request.method == 'POST':
        rem_form = RemmitForm(request.POST, instance=remit)
        receiver_form = ReceiverForm(request.POST, instance=client)
        if rem_form.is_valid() and receiver_form.is_valid():
            remitt = rem_form.save()
            receiver_form.save()
            new_req = Requestpay()
            new_req.remittance = remitt
            new_req.created_by = request.user
            new_req.ip = get_client_ip(request)
            new_req.save()
            req.resubmit_flag=True
            req.save()
            messages.info(request, 'This request is successfully resubmitted')
            return redirect('show_req')
        else:
            context = {'form': receiver_form, 'rform': rem_form}
    else:
        rem_form = RemmitForm(instance=remit)
        receiver_form = ReceiverForm(instance=client)
        context = {'form': receiver_form, 'rform': rem_form, 'comment':req.comment}
    return render(request,'rem/forms/remmit_resubmit.html',context)


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.employee.branch = form.cleaned_data.get('branch')
            user.employee.cell = form.cleaned_data.get('cell')
            user.save()
            #raw_password = form.cleaned_data.get('password1')
            #user = authenticate(username=user.username, password=raw_password)
            #login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

###################### django-registration views ##################################################
@method_decorator([transaction.atomic,], name='dispatch')
class UserRegistrationView(RegistrationView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'

    """def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.branch = self.request.user.employee.branch
        receiver = get_object_or_404(Receiver, pk=self.kwargs['pk'])
        form.instance.receiver = receiver
        self.object = form.save(commit=False)
        # in case you want to modify the object before commit
        self.object.save()
        req = Requestpay(remittance=self.object, created_by=self.request.user, ip=get_client_ip(self.request))
        req.save()
        return super().form_valid(form)"""

    def register(self,form):
        new_user = super(UserRegistrationView,self).create_inactive_user(form)
        new_user.refresh_from_db()
        branch= form.cleaned_data.get('branch')
        cell = form.cleaned_data.get('cell')
        #new_user.employee.branch = branch
        #new_user.employee.cell = cell
        employee =Employee.objects.create(user=new_user, branch=branch, cell=cell)
        # set here all other values
        new_user.save()
        employee.save()
        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
            )
        return new_user

############################################# Only information Update #########################################################

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitInfoCreate(SuccessMessageMixin, CreateView):
    model = Remmit
    form_class = RemittInfoForm
    template_name = 'rem/forms/remmit_info_form.html'
    success_message = "Remittance information was submitted successfully"
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
        req = Requestpay(remittance=self.object, created_by=self.request.user, status='PD', ip=get_client_ip(self.request))
        req.save()
        req.refresh_from_db()
        payment = Payment(requestpay=req, paid_by=self.request.user, agent_screenshot=self.request.FILES.get('screenshot',False), ip=get_client_ip(self.request))
        payment.save()
        return super().form_valid(form)

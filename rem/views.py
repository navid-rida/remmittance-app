from django.shortcuts import render,redirect, get_object_or_404#, render_to_response
from django.http import HttpResponse
from .forms import RemmitForm, SearchForm, ReceiverSearchForm, ReceiverForm, PaymentForm, SignUpForm, RemittInfoForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Remmit, Requestpay, Payment, Receiver,Employee, ReceiverUpdateHistory,RemittanceUpdateHistory, Branch, Booth
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
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
############################### djang-registration imports ##########################
from django_registration.backends.activation.views import RegistrationView
from django_registration import signals
################################ Reports ######################
from .summary_report import exchange_housewise_remittance_summary
############################ Rules and Permissions #########################
from rules.contrib.views import PermissionRequiredMixin, permission_required
#from rules.contrib.views import permission_required
import rem.rule_set
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

"""@login_required
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
                req_list = Requestpay.objects.filter(**filter_args).order_by('remittance__exchange','-datecreate','remittance__branch__code')
                context = {'pay_list': req_list, 'form':form}
                return render(request, 'rem/report/payment_list_ho.html', context)
            else:
                filt['remittance__branch'] = request.user.employee.branch
                filter_args = {k:v for k,v in filt.items() if v is not None}
                req_list = Requestpay.objects.filter(**filter_args).order_by('remittance__exchange','-datecreate','remittance__branch__code')
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
            return render(request, 'rem/report/payment_list_branch.html', context)"""

@login_required
def show_rem(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        #filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            """if (date_from != None) and (date_to!= None):
                filt['datecreate__date__range'] = (date_from,date_to)
            else:
                filt['datecreate__date__range'] = None"""
            exchange_house = form.cleaned_data['exchange']
            #filt['status'] = 'PD'
            branch = form.cleaned_data['branch']
            booth = form.cleaned_data['booth']
            #filt['resubmit_flag'] = False
            #filter_args = {k:v for k,v in filt.items() if v is not None}
            req_list = request.user.employee.get_related_remittance(start_date=date_from, end_date= date_to, branch= branch, booth= booth, exchange_house=exchange_house)
            context = {'pay_list': req_list, 'form':form}
            if check_headoffice(request.user):
                return render(request, 'rem/report/payment_list_ho.html', context)
            else:
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
            rem_list = Payment.objects.filter(**filter_args).order_by('requestpay__remittance__exchange','-dateresolved','requestpay__remittance__branch__code')
            if rem_list:
                #df = qset_to_df(rem_list)
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
def select_cash_incentive_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        filt = {}
        if form.is_valid():
            #date_from = form.cleaned_data['date_from']
            #date_to = form.cleaned_data['date_to']
            filt['requestpay__remittance__exchange'] = form.cleaned_data['exchange']
            filt['requestpay__remittance__branch'] = form.cleaned_data['branch']
            filt['requestpay__remittance__cash_incentive_status'] = 'P'
            filt['requestpay__remittance__date_cash_incentive_settlement__isnull'] = True
            filter_args = {k:v for k,v in filt.items() if v is not None}
            rem_list = Payment.objects.filter(**filter_args).order_by('requestpay__remittance__exchange','-dateresolved','requestpay__remittance__branch__code')
            if rem_list:
                #df = qset_to_df(rem_list)
                #ids = list(df['id'][df.duplicated(['amount','branch_id','exchange_id'],keep=False)==True].values)
                context = {'rem_list': rem_list, 'form':form}
            else:
                context = {'form':form}
        else:
            context = {'form':form}
    else:
        form = SearchForm()
        context = {'form':form}

    return render(request, 'rem/report/cash_incentive_excel.html', context)


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
            rem_list = Payment.objects.filter(**filter_args).order_by('requestpay__remittance__exchange','-dateresolved','requestpay__remittance__branch__code')
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/mark_settle.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/mark_settle.html', context)

@login_required
@user_passes_test(check_headoffice)
def mark_cash_incentive_list(request):
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
            filt['requestpay__remittance__cash_incentive_status']  = 'P'
            filt['requestpay__remittance__date_cash_incentive_settlement__isnull'] = True
            filter_args = {k:v for k,v in filt.items() if v is not None}
            rem_list = Payment.objects.filter(**filter_args).order_by('requestpay__remittance__exchange','-dateresolved','requestpay__remittance__branch__code')
            context = {'rem_list': rem_list, 'form':form}
            return render(request, 'rem/report/cash_incentive_mark_settle.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
    return render(request, 'rem/report/mark_settle.html', context)


@login_required
@permission_required('rem.add_remmit')
#@user_passes_test(check_branch)
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
class ReceiverUpdate(PermissionRequiredMixin, UpdateView):
    model = Receiver
    permission_required = 'rem.change_reciver'
    form_class = ReceiverForm
    template_name = 'rem/forms/receiver_edit_form.html'
    #success_url = reverse_lazy('remmit-create',args=(self.object.id,))

    """def test_func(self):
        id = int(self.kwargs['pk'])
        receiver = Receiver.objects.get(pk=id)
        user = receiver.created_by
        if self.request.user == user:
            return True
        else:
            return False"""

    def get_success_url(self):
        return reverse('remmit-create-with-payment', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        update = ReceiverUpdateHistory()
        update.receiver= self.object
        update.createdby = self.request.user
        update.ip = get_client_ip(self.request)
        update.save()
        return super().form_valid(form)

@login_required
@user_passes_test(check_headoffice)
def download_selected_excel(request):
    if request.method == 'POST' and request.POST.getlist('checks'):
        list = request.POST.getlist('checks') # If the form has been submitted...
        #form = Remmit.objects.filter(id__in=selected_values)
        payments = Payment.objects.order_by('requestpay__remittance__exchange','dateresolved','requestpay__remittance__branch__code')
        df = rem_bb_summary(list, payments)
        xlsx_data = excel_output(df)
        response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        time = str(timezone.now().date())
        filename = "batch "+time+".xlsx"
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        #writer.save(re)
        return response
    else:
        form = SearchForm()
        list = "Please select at least one entry " # An unbound form
    return redirect('select_rem_list')

@login_required
@user_passes_test(check_headoffice)
def download_cash_incentive_excel(request):
    if request.method == 'POST' and request.POST.getlist('checks'):
        list = request.POST.getlist('checks') # If the form has been submitted...
        #form = Remmit.objects.filter(id__in=selected_values)
        payments = Payment.objects.order_by('requestpay__remittance__exchange','dateresolved','requestpay__remittance__branch__code')
        df = cash_incentive_df(list, payments)
        xlsx_data = excel_output(df)
        response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        time = str(timezone.now().date())
        filename = "Cash Incentive Batch "+time+".xlsx"
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        #writer.save(re)
        return response
    else:
        form = SearchForm()
        list = "Please select at least one entry " # An unbound form
    return redirect('select-cash-incentive')

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
            entry.date_settle = timezone.now()
            entry.settled_by=request.user
            entry.save()
    return redirect('mark_rem_list')

@login_required
@user_passes_test(check_headoffice)
@transaction.atomic
def cash_incentive_mark_settle(request):
    if request.method == 'POST':
        list = request.POST.getlist('checks') # If the form has been submitted...
        #form = Remmit.objects.filter(id__in=selected_values)
        """messages.info(request, 'This request is successfully resubmitted'+list[0])
        return redirect('show_req')"""
        for id in list:
            entry = Payment.objects.get(pk=id)
            #entry.requestpay.remittance.cash_incentive_status = 'S'
            entry.requestpay.remittance.date_cash_incentive_settlement = timezone.now().date()
            #entry.settled_by=request.user
            entry.requestpay.remittance.save()
            entry.save()
    return redirect('mark_cash_incentive_list')

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

@method_decorator([login_required,], name='dispatch')
class RemmitDetailView(DetailView):
    model = Remmit
    template_name = 'rem/detail/remmit_detail_base.html'

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
        booth = form.cleaned_data.get('booth')
        #new_user.employee.branch = branch
        #new_user.employee.cell = cell
        employee =Employee.objects.create(user=new_user, branch=branch, cell=cell, booth=booth)
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
    #permission_required = 'rem.add_remmit'
    form_class = RemittInfoForm
    template_name = 'rem/forms/remmit_info_form.html'
    success_message = "Remittance information was submitted successfully"
    success_url = reverse_lazy('index')

    """def get_success_url(self):
        return reverse('add_req', kwargs={'pk': self.object.id})"""

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.branch = self.request.user.employee.branch
        if self.request.user.employee.booth:
            form.instance.booth = self.request.user.employee.booth
        receiver = get_object_or_404(Receiver, pk=self.kwargs['pk'])
        form.instance.receiver = receiver
        form.instance.cash_incentive_amount = form.instance.amount*Decimal(0.02)
        self.object = form.save(commit=False)
        # in case you want to modify the object before commit
        self.object.save()
        req = Requestpay(remittance=self.object, created_by=self.request.user, status='PD', ip=get_client_ip(self.request))
        req.save()
        req.refresh_from_db()
        payment = Payment(requestpay=req, paid_by=self.request.user, agent_screenshot=self.request.FILES.get('screenshot',False), ip=get_client_ip(self.request))
        payment.save()
        return super().form_valid(form)

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitInfoUpdate(PermissionRequiredMixin, UpdateView):

    """def test_func(self):
        id = int(self.kwargs['pk'])
        remittance = Remmit.objects.get(pk=id)
        user = remittance.created_by
        if self.request.user == user:
            return True
        else:
            return False"""

    model = Remmit
    permission_required = 'rem.change_remmit'
    form_class = RemittInfoForm
    template_name = 'rem/forms/remmit_info_update_form.html'
    success_url = reverse_lazy('show_rem')

    def form_valid(self, form):
        form.instance.cash_incentive_amount = form.instance.amount*Decimal(0.02)
        self.object = form.save(commit=False)
        # in case you want to modify the object before commit
        self.object.save()
        payment = self.object.get_completed_payment()
        payment.agent_screenshot = self.request.FILES.get('screenshot',False)
        payment.save()
        update = RemittanceUpdateHistory()
        update.remittance= self.object
        update.createdby = self.request.user
        update.ip = get_client_ip(self.request)
        update.save()
        return super().form_valid(form)


################################ Reports ################################

@login_required
@permission_required('rem.view_ho_br_booth_reports')
def summary_report(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            exchange = form.cleaned_data['exchange']
            BranchBooth = form.cleaned_data['BranchBooth']
            lst=Branch.objects.none().order_by('code') # This will contain branch or booth list for summary function
            if BranchBooth=='branch' or BranchBooth=='all':
                lst = Branch.objects.all().order_by('code')
                #summary_list = branch_remittance_summary(branch_list, start_date=date_from, end_date= date_to, exchange_house= exchange)
            elif BranchBooth=='booth':
                lst = Booth.objects.all().order_by('code')
            summary_list = exchange_housewise_remittance_summary(lst, start_date=date_from, end_date= date_to, exchange_house= exchange, BranchBooth=BranchBooth)
            if '_show' in request.POST:
                context = {'form':form, 'df': summary_list, }
                return render(request, 'rem/report/summary/summary_base.html', context)
            elif '_download' in request.POST:
                df = pd.DataFrame(summary_list, columns=['code','name','count','sum'])
                xlsx_data = excel_output(df)
                response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                time = str(timezone.now().date())
                filename = "summary report "+time+".xlsx"
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                #writer.save(re)
                return response
        else:
            context = {'form':form }
            return render(request, 'rem/report/summary/summary_base.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        return render(request, 'rem/report/summary/summary_base.html', context)

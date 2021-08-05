from __future__ import unicode_literals

from django.shortcuts import render,redirect, get_object_or_404#, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse
from .forms import RemmitForm, SearchForm, ReceiverSearchForm, ReceiverForm, PaymentForm, SignUpForm, RemittInfoForm, SettlementForm, MultipleSearchForm, ClaimForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Remmit, Requestpay, Payment, Receiver,Employee, ReceiverUpdateHistory,RemittanceUpdateHistory, Branch, Booth, Claim, CashIncentive
from django.db.models import Sum, Count
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
from .summary_report import exchange_housewise_remittance_summary, cash_incentive_bb_statement
############################ Rules and Permissions #########################
from rules.contrib.views import PermissionRequiredMixin, permission_required, objectgetter
#from rules.contrib.views import permission_required
import rem.rule_set
import rules
##################### Searching#########################
from rem.search import remittance_search
# Create your views here.
from schedules.data import get_daily_bb_remittance


from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

from pathlib import Path

MAXIMUM_AllOWWED_USER_PER_BRANCH = settings.MAXIMUM_USER_PER_BRANCH

###############User tests############################
"""def check_user_available(branch, MAXIMUM_AllOWWED_USER_PER_BRANCH):
    number = branch.employee_set.all().count()
    if number >= MAXIMUM_AllOWWED_USER_PER_BRANCH:
        return False
    else:
        return True"""

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Remmit
    form_class = RemmitForm
    permission_required = ['rem.add_remmit','rem.allow_if_transaction_hour']
    template_name = 'rem/forms/remmit_create_form.html'
    success_message = "Remittance request was submitted successfully"
    success_url = reverse_lazy('index')

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
        if self.object.cash_incentive_status=='P':
            self.object.date_cash_incentive_paid=timezone.now()
        self.object.save()
        req = Requestpay(remittance=self.object, created_by=self.request.user, ip=get_client_ip(self.request))
        req.save()
        return super().form_valid(form)

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitUpdate(PermissionRequiredMixin, SuccessMessageMixin,UpdateView):
    model = Remmit
    form_class = RemmitForm
    permission_required = ['rem.change_remmit','rem.allow_if_transaction_hour']
    template_name = 'rem/forms/remmit_update_form.html'
    success_message = "Remittance request was updated successfully"
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
            keyword = form.cleaned_data['keyword']
            BranchBooth = form.cleaned_data['BranchBooth']
            #filt['resubmit_flag'] = False
            #filter_args = {k:v for k,v in filt.items() if v is not None}
            req_list = request.user.employee.get_related_remittance(start_date=date_from, end_date= date_to, branch= branch, booth= booth, exchange_house=exchange_house, keyword=keyword, BranchBooth=BranchBooth)
            if '_show' in request.POST:
                sum_n_count = req_list.values('exchange__name').order_by('exchange').annotate(total=Sum('amount')).annotate(number = Count('amount'))
                context = {'pay_list': req_list, 'form':form, 'sum_n_count':sum_n_count}
                """if check_headoffice(request.user):
                    return render(request, 'rem/report/payment_list_ho.html', context)
                else:
                    return render(request, 'rem/report/payment_list_branch.html', context)"""
                if request.user.has_perm('rem.view_ho_br_booth_reports'):
                    return render(request, 'rem/report/payments/payment_list_ho.html', context)
                else:
                    return render(request, 'rem/report/payments/payment_list_branch.html', context)
            if '_download' in request.POST:
                #df = pd.DataFrame(summary_list, columns=['code','name','count','sum'])
                df = pd.DataFrame(list(req_list.values('branch__name','branch__code','booth__name', \
                 'booth__code','exchange__name','currency__name','rem_country__name', \
                 'sender','sender_occupation','relationship','purpose','cash_incentive_status', \
                 'unpaid_cash_incentive_reason','receiver__name','receiver__idno', \
                 'amount','cash_incentive_amount','date_sending','date_cash_incentive_paid', \
                 'date_cash_incentive_settlement','date_create','reference','created_by')))
                xlsx_data = excel_output(df)
                response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                time = str(timezone.now().date())
                filename = "Remittance List "+time+".xlsx"
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                #writer.save(re)
                return response
        else:
            context = {'form':form }
            if check_headoffice(request.user):
                return render(request, 'rem/report/payments/payment_list_ho.html', context)
            else:
                return render(request, 'rem/report/payments/payment_list_branch.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        if check_headoffice(request.user):
            return render(request, 'rem/report/payments/payment_list_ho.html', context)
        else:
            return render(request, 'rem/report/payments/payment_list_branch.html', context)


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
            filt['remittance__exchange'] = form.cleaned_data['exchange']
            filt['remittance__branch'] = form.cleaned_data['branch']
            filt['entry_category'] = 'P'
            filt['date_cash_incentive_settlement__isnull'] = True
            filter_args = {k:v for k,v in filt.items() if v is not None}
            rem_list = CashIncentive.objects.filter(**filter_args).order_by('remittance__exchange','-date_cash_incentive_paid','remittance__branch__code')
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


""""@login_required
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
    return render(request, 'rem/report/mark_settle.html', context)"""

"""@login_required
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
    return render(request, 'rem/report/mark_settle.html', context)"""


@login_required
@permission_required(['rem.add_remmit','rem.allow_if_transaction_hour'])
#@user_passes_test(check_branch)
#@user_passes_test(check_headoffice)
def search_receiver(request):
    if request.method == "POST":
        form = ReceiverSearchForm(request.POST)
        if form.is_valid():
            identification = form.cleaned_data['identification']
            try:
                receiver = Receiver.objects.get(idno=identification)
                if receiver.check_incomplete_info():
                    messages.info(request, 'It seems that the customer information is incomplete. Please update the appropriate fields')
                    return redirect('receiver_update', receiver.id)
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

@login_required
#@user_passes_test(check_branch)
#@user_passes_test(check_headoffice)
def search_remittance(request):
    context={}
    if request.method == "POST":
        form = MultipleSearchForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            q = Remmit.objects.all()
            q = remittance_search(keyword,q)
            context = {'form':form,'rem_list':q}
            return render(request, 'rem/process/remittance_search.html', context)
        else:
            context = {'form':form}
    else:
        form = MultipleSearchForm()
        context = {'form':form}
    return render(request, 'rem/process/remittance_search.html', context)

@method_decorator([login_required,transaction.atomic],name='dispatch')
class ReceiverCreate(PermissionRequiredMixin,SuccessMessageMixin, CreateView):
    model = Receiver
    form_class = ReceiverForm
    permission_required = ['rem.allow_if_transaction_hour','rem.add_remmit']
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
class ReceiverUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Receiver
    permission_required = ['rem.allow_if_transaction_hour']
    form_class = ReceiverForm
    template_name = 'rem/forms/receiver_edit_form.html'
    success_message = "Customer was updated successfully"
    #success_url = reverse_lazy('remmit-create',args=(self.object.id,))


    def get_success_url(self):
        return reverse('search_client')

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
        ci = CashIncentive.objects.order_by('remittance__exchange','date_cash_incentive_paid','remittance__branch__code')
        df = cash_incentive_df(list, ci)
        xlsx_data = excel_output(df)
        response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        time = str(timezone.now().date())
        filename = "Cash In "+time+".xlsx"
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
        done_list=Payment.objects.filter(id__in=list)
        form = SearchForm()
        context = {'done_list': done_list, 'form':form}
        return render(request, 'rem/report/mark_settle.html', context)
    #return redirect('mark_rem_list')

@login_required
@user_passes_test(check_headoffice)
@transaction.atomic
def mark_settle_all(request):
    context={}
    if request.method == 'POST':
        form = SettlementForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES.get('batchfile')
            settlement_type = request.POST['settlemnt_type']
            df = pd.read_excel(file,names=['date', 'branch_code', 'ac_no', 'type', 'amount', 'narrations', 'flags'], header=None)
            if clean_settlement_df(df):
                lst = clean_settlement_df(df)
                for n in lst:
                    messages.error(request, "Row "+str(n+1)+" have missing element in one or more cells")
                return redirect('mark_settle_all')
            df['reference'] = df['narrations'].apply(get_reference_no_from_narration)
            lst = get_reference_no_list_from_df(df)
            if settlement_type=='remittance':
                q = Payment.objects.filter(requestpay__remittance__reference__in=lst)
                for item in q:
                    ref = item.requestpay.remittance.reference
                    item = item.settle_remittance(user=request.user)
                    if item:
                        item.save()
                        messages.success(request, ref+" Successfully Settled")
                    else:
                        messages.error(request, ref+' Cannot be settled')
            elif settlement_type=='cash_incentive':
                q = Remmit.objects.filter(reference__in=lst)
                for item in q:
                    ref = item.reference
                    item = item.settle_cash_incentive()
                    if item:
                        item.save()
                        messages.success(request, ref+" Cash Incentive Successfully Settled")
                    else:
                        messages.error(request, ref+' Cash Incentive Cannot be settled')

            context = {'list': lst, 'form':form}
    else:
        form = SettlementForm()
        context = {'form':form}
    return render(request, 'rem/process/settlement/settlement_base.html', context)

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
        done_list=Payment.objects.filter(id__in=list)
        form = SearchForm()
        context = {'done_list': done_list, 'form':form}
        return render(request, 'rem/report/cash_incentive_mark_settle.html', context)
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
class RemmitInfoCreate(PermissionRequiredMixin,SuccessMessageMixin, CreateView):
    model = Remmit
    permission_required = ['rem.add_remmit','rem.allow_if_transaction_hour']
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
        if self.object.cash_incentive_status=='P':
            self.object.date_cash_incentive_paid=timezone.now()
        self.object.save()
        req = Requestpay(remittance=self.object, created_by=self.request.user, status='PD', ip=get_client_ip(self.request))
        req.save()
        req.refresh_from_db()
        payment = Payment(requestpay=req, paid_by=self.request.user, agent_screenshot=self.request.FILES.get('screenshot',False), ip=get_client_ip(self.request))
        payment.save()
        return super().form_valid(form)

@method_decorator([login_required,transaction.atomic], name='dispatch')
class RemmitInfoUpdate(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):

    """def test_func(self):
        id = int(self.kwargs['pk'])
        remittance = Remmit.objects.get(pk=id)
        user = remittance.created_by
        if self.request.user == user:
            return True
        else:
            return False"""

    model = Remmit
    permission_required = ['rem.change_remmit','rem.allow_if_transaction_hour']
    form_class = RemittInfoForm
    template_name = 'rem/forms/remmit_info_update_form.html'
    success_url = reverse_lazy('show_rem')
    success_message = "Remittance information was updated successfully"
    

    def get_initial(self):
        entry_category = self.object.cashincentive_set.last().entry_category
        reason_a = self.object.cashincentive_set.last().unpaid_cash_incentive_reason
        return {'entry_category': entry_category, 'reason_a': reason_a}

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

@login_required
@permission_required(['rem.can_mark_paid_remittance','rem.allow_if_transaction_hour'], fn=objectgetter(Remmit, 'pk'))
@transaction.atomic
def pay_unpaid_incentive(request, pk):
    rem = Remmit.objects.get(pk=pk)
    result = rem.pay_previously_unpaid_cash_incentive()
    if result:
        update = RemittanceUpdateHistory()
        update.remittance= result
        update.createdby = request.user
        update.ip = get_client_ip(request)
        update.save()
        messages.success(request, 'Cash incentive now marked as paid')
        return redirect('show_rem')
    else:
        messages.warning(request, 'Cannot process the request right now')
        return redirect('show_rem')
    #return render(request,'rem/forms/remmit_resubmit.html',context)

@login_required
@permission_required(['rem.view_trm_form'], fn=objectgetter(Remmit, 'pk'))
@transaction.atomic
def download_trm(request, pk):
    rem = get_object_or_404(Remmit, pk=pk)
    context = {'rem': rem}
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline; filename={date}-{name}-trm form.pdf".format(
        date=timezone.now(),
        name=rem.reference,
    )
    html = render_to_string("rem/detail/trm.html", context)
    #result = rem.pay_previously_unpaid_cash_incentive()
    #return render(request, 'rem/detail/trm.html', context)

    font_config = FontConfiguration()
    css_path = Path(settings.STATIC_ROOT,'css/bootstrap/bootstrap.css')
    css = CSS(css_path)
    HTML(string=html).write_pdf(response, stylesheets=[css], font_config=font_config)
    return response


@login_required
@permission_required(['rem.view_trm_form'], fn=objectgetter(Remmit, 'pk'))
@transaction.atomic
def download_voucher(request, pk):
    rem = get_object_or_404(Remmit, pk=pk)
    taka, ps = (str(int(rem.amount//1)), "0"+str(int(Decimal(rem.amount%1)*100)) if int(Decimal(rem.amount%1)*100)<10 else str(int(Decimal(rem.amount%1)*100)) )
    cash_incentive_taka, cash_incentive_ps = (str(int(rem.cash_incentive_amount//1)), "0"+str(int(Decimal(rem.cash_incentive_amount%1)*100)) if int(Decimal(rem.cash_incentive_amount%1)*100)<10 else str(int(Decimal(rem.cash_incentive_amount%1)*100))) if not rem.check_unpaid_cash_incentive() else (0,0)
    context = {'rem': rem, 'taka':taka, 'ps':ps, 'cash_incentive_taka': cash_incentive_taka, 'cash_incentive_ps': cash_incentive_ps, 'user':request.user}
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline; filename={date}-{name}-voucher.pdf".format(
        date=timezone.now(),
        name=rem.reference,
    )
    html = render_to_string("rem/detail/voucher.html", context)
    #result = rem.pay_previously_unpaid_cash_incentive()
    #return render(request, 'rem/detail/trm.html', context)

    font_config = FontConfiguration()
    css_path = Path(settings.STATIC_ROOT,'css/bootstrap/bootstrap.css')
    css = CSS(css_path)
    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=[css], font_config=font_config)
    return response
    #return render(request, 'rem/detail/voucher.html', context)

@login_required
@permission_required(['rem.view_trm_form', 'rem.can_view_cash_incentive_undertaking'], fn=objectgetter(Remmit, 'pk'), raise_exception=True)
@transaction.atomic
def download_undertaking(request, pk):
    rem = get_object_or_404(Remmit, pk=pk)
    context = {'rem': rem}
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline; filename={date}-{name}-undertaking.pdf".format(
        date=timezone.now(),
        name=rem.reference,
    )
    html = render_to_string("rem/detail/undertaking.html", context)
    #result = rem.pay_previously_unpaid_cash_incentive()
    #return render(request, 'rem/detail/trm.html', context)

    font_config = FontConfiguration()
    css_path = Path(settings.STATIC_ROOT,'css/bootstrap/bootstrap.css')
    css = CSS(css_path)
    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=[css], font_config=font_config)
    return response

#####################################Claim Create and Update#########################
@method_decorator([login_required,transaction.atomic], name='dispatch')
class ClaimCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Claim
    form_class = ClaimForm
    permission_required = ['rem.add_remmit','rem.allow_if_transaction_hour']
    template_name = 'rem/forms/claim_create_form.html'
    success_message = "Claim was submitted successfully"
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.branch = self.request.user.employee.branch
        self.object = form.save(commit=False)
        # in case you want to modify the object before commit
        self.object.save()
        return super().form_valid(form)

@login_required
def show_claim(request):
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
            #exchange_house = form.cleaned_data['exchange']
            #filt['status'] = 'PD'
            branch = form.cleaned_data['branch']
            booth = form.cleaned_data['booth']
            #keyword = form.cleaned_data['keyword']
            #filt['resubmit_flag'] = False
            #filter_args = {k:v for k,v in filt.items() if v is not None}
            claim_list = request.user.employee.get_related_claim(start_date=date_from, end_date= date_to, branch= branch, booth= booth)
            if '_show' in request.POST:
                context = {'claim_list': claim_list, 'form':form}
                return render(request, 'rem/report/claim/claim_list_base.html', context)
            if '_download' in request.POST:
                #df = pd.DataFrame(summary_list, columns=['code','name','count','sum'])
                #df = pd.DataFrame(list(claim_list.values()))
                df = make_claim_df(claim_list)
                xlsx_data = excel_output(df)
                response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                time = str(timezone.now().date())
                filename = "Claim List "+time+".xlsx"
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                #writer.save(re)
                return response
        else:
            context = {'form':form }
            return render(request, 'rem/report/claim/claim_list_base.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        return render(request, 'rem/report/claim/claim_list_base.html', context)

@method_decorator([login_required,], name='dispatch')
class ClaimDetailView(DetailView):
    model = Claim
    template_name = 'rem/detail/claim_detail_base.html'

    """def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PaymentForm()
        return context"""

@login_required
#@permission_required(['rem.can_mark_paid_remittance','rem.allow_if_transaction_hour'], fn=objectgetter(Remmit, 'pk'))
@transaction.atomic
def forward_claim(request, pk):
    claim = Claim.objects.get(pk=pk)
    result = claim.forward_claim()
    if result:
        messages.success(request, 'Cash incentive claim forwarded')
        return redirect('show_claim')
    else:
        messages.warning(request, 'Claim is either already forwarded or resolved')
        return redirect('show_claim')

@login_required
#@permission_required(['rem.can_mark_paid_remittance','rem.allow_if_transaction_hour'], fn=objectgetter(Remmit, 'pk'))
@transaction.atomic
def mark_resolved(request, pk):
    claim = Claim.objects.get(pk=pk)
    result = claim.mark_resolved()
    if result:
        messages.success(request, 'Cash incentive claim marked as realized')
        return redirect('show_claim')
    else:
        messages.warning(request, 'Claim is either NOT forwarded or  already resolved')
        return redirect('show_claim')
################################ Reports ################################

@login_required
#@permission_required('rem.view_ho_br_booth_reports')
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
                if request.user.has_perm('rem.view_ho_br_booth_reports'):
                    lst = Branch.objects.all().order_by('code')
                elif request.user.has_perm('rem.view_branch_remitt'):
                    lst = Branch.objects.filter(code=request.user.employee.branch.code).order_by('code')
                else:
                    lst=Branch.objects.none().order_by('code')
                #summary_list = branch_remittance_summary(branch_list, start_date=date_from, end_date= date_to, exchange_house= exchange)
            elif BranchBooth=='booth':
                if request.user.has_perm('rem.view_ho_br_booth_reports'):
                    lst = Booth.objects.all().order_by('code')
                elif request.user.has_perm('rem.view_branch_remitt'):
                    lst = Booth.objects.filter(branch=request.user.employee.branch).order_by('code')
                elif request.user.has_perm('rem.view_booth_remitt'):
                    lst = Booth.objects.filter(code=request.user.employee.booth.code).order_by('code')
                else:
                    lst=Booth.objects.none().order_by('code')
            else:
                if request.user.has_perm('rem.view_booth_remitt') and request.user.employee.booth:
                    lst = Booth.objects.filter(code=request.user.employee.booth.code).order_by('code')
                else:
                    lst=Booth.objects.none().order_by('code')
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

@login_required
@permission_required('rem.view_ho_br_booth_reports')
def monthly_cash_incentive_bb_statement(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        #filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            query_set = Remmit.objects.all()
            #q = filter_remittance(query_set, start_date=date_from, end_date= date_to, cash_incentive_status='P', cash_incentive_settlement_done=True)
            q = query_set.filter(date_cash_incentive_settlement__range=(date_from,date_to),cash_incentive_status='P',date_cash_incentive_settlement__isnull=False)
            statement = cash_incentive_bb_statement(qset=q)
            if '_show' in request.POST:
                context = {'form':form, 'df': statement, }
                return render(request, 'rem/report/cash_incentive_bb_statement/cash_incentive_base.html', context)
            if '_download' in request.POST:
                #df = pd.DataFrame(summary_list, columns=['code','name','count','sum'])
                xlsx_data = excel_output(statement)
                response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                time = str(timezone.now().date())
                filename = "cash incentive statement "+time+".xlsx"
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                #writer.save(re)
                return response
        else:
            context = {'form':form }
            return render(request, 'rem/report/cash_incentive_bb_statement/cash_incentive_base.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        return render(request, 'rem/report/cash_incentive_bb_statement/cash_incentive_base.html', context)

@login_required
@permission_required('rem.view_ho_br_booth_reports')
def daily_remittance_bb_statement(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        #filt = {}
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            query_set = Payment.objects.all()
            if date_from and date_to:
                query_set = query_set.filter(dateresolved__date__range=(date_from,date_to))
            #q = filter_remittance(query_set,start_date=date_from, end_date= date_to)
            #q = filter_remittance(query_set, start_date=date_from, end_date= date_to, cash_incentive_status='P', cash_incentive_settlement_done=True)
            #q = query_set.filter(dateresolved__date__range=(date_from,date_to))
            statement = get_daily_bb_remittance(qset=query_set)
            if '_show' in request.POST:
                context = {'form':form, 'df': statement, 'q':query_set}
                return render(request, 'rem/report/cash_incentive_bb_statement/daily_remittance_bb_base.html', context)
            if '_download' in request.POST:
                #df = pd.DataFrame(summary_list, columns=['code','name','count','sum'])
                xlsx_data = excel_output(statement)
                response = HttpResponse(xlsx_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                time = str(timezone.now().date())
                filename = "Daily Statement BB "+time+".xlsx"
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                #writer.save(re)
                return response
        else:
            context = {'form':form }
            return render(request, 'rem/report/cash_incentive_bb_statement/daily_remittance_bb_base.html', context)
    else:
        form = SearchForm()
        context = {'form':form}
        return render(request, 'rem/report/cash_incentive_bb_statement/daily_remittance_bb_base.html', context)

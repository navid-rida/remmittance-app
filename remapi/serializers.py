from django.db.models.query import QuerySet
from rest_framework import serializers
from django.contrib.auth.models import User
from rem.models import Receiver, Remmit, Country, ExchangeHouse, Branch, Booth
from schedules.models import Currency
from rem.validators import *
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone

from django.db import transaction


########### Permissions ######################


class ReceiverSerializer(serializers.ModelSerializer):
    #nationality = serializers.SlugRelatedField(queryset=Country.objects.all(), slug_field ='name')

    class Meta:
        model=Receiver
        fields = ['name','gender','father_name','mother_name','spouse_name'
                    ,'ac_no','address','dob','cell','idtype','idissue','idexpire',
                    'idno']

    def validate_ac_no(self, value):
        """
        Check if the account is valid nrbc account
        """
        if value:
            try:
                nrbc_acc(value)
            except Exception as e:
                raise serializers.ValidationError(e.message)
        return value

    def validate_cell(self,value):
        try:
            mobile_re(value)
        except Exception as e:
            raise serializers.ValidationError(e.message)
        return value

    def validate_idexpire(self, day):
        today = datetime.date.today()
        if day and day<today:
            raise serializers.ValidationError(_('ID Expired'))
        return day


    def validate_dob(self, day):
        """
        Return exceptions if date sending is in future
        """
        today = datetime.date.today()
        if day>=today:
            raise serializers.ValidationError(_('Birthday must be a past date'))
        return day

    def validate(self, data):
        father = data['father_name']
        spouse = data['spouse_name']
        gender = data['gender']
        idno = data['idno']
        idtype = data['idtype']
        idissue = data['idissue']
        idexpire = data['idexpire']
        if (gender=='M' or gender=='O') and not father:
            raise serializers.ValidationError({'father_name':_('Father\'s name is mandatory')})
        if gender == 'F' and (not father) and (not spouse):
            raise serializers.ValidationError(_('Father\'s and/or Husband\'s name is mandatory'))
        if idtype == 'NID':
            if len(idno)<13:
                validate_smart_nid(idno)
            else:
                validate_old_nid(idno)
        elif idtype=='PASSPORT':
            if not idissue:
                raise serializers.ValidationError({'idissue':_('Issue date is mandatory for passport')})
            if not idexpire:
                raise serializers.ValidationError({'idexpire':_('Expiry date is mandatory for passport')})
            validate_passport(idno)
        elif idtype=='DL':
            if not idissue:
                raise serializers.ValidationError({'idissue':_('Issue date is mandatory for Driving License')})
            if not idexpire:
                raise serializers.ValidationError({'idexpire':_('Expiry date is mandatory for Driving License')})
            validate_alpha_num(idno)
        else:
            if not idissue:
                raise serializers.ValidationError({'idissue':_('Issue date is mandatory for Birth Certificate')})
            validate_bc(idno)

        if idissue and idexpire and idissue>idexpire:
            raise serializers.ValidationError({'idexpire':_('Id issue date cannot after Id expire date')})
        return data

    

def is_sub_branch_under_branch(sub_branch,branch):

    # Checks if a sub branch code is under a branch code
    # Returns True if sub branch is under given branch
    #sub_branch = Booth.objects.get(code=sub_branch_code)
    if sub_branch.branch == branch:
        return True
    else:
        return False

class RemmitSerializer(serializers.ModelSerializer):
    exchange = serializers.SlugRelatedField(queryset=ExchangeHouse.objects.all(), slug_field ='name')
    rem_country = serializers.SlugRelatedField(queryset=Country.objects.all(), slug_field ='name')
    currency = serializers.SlugRelatedField(queryset=Currency.objects.all(), slug_field='short')
    receiver = serializers.SlugRelatedField(queryset=Receiver.objects.all(), slug_field ='idno')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='code')
    #image = serializers.CharField(max_length=100)
    sub_branch = serializers.SlugRelatedField(queryset=Booth.objects.all(), slug_field='code', source='booth')
    #created_by = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model=Remmit
        fields=['receiver','exchange','branch','sub_branch','rem_country','reference','sender','sender_occupation',
                'sender_gender','amount', 'currency','relationship', 'purpose', 'date_sending',
                'cash_incentive_status','unpaid_cash_incentive_reason', 'screenshot']

    def validate_currency(self, value):
        """
        Check if the currency is BDT
        """
        if value.short != 'BDT':
            raise serializers.ValidationError(_('Currency must be BDT'))
        return value

    def validate_date_sending(self, day):
        """
        Return exceptions if date sending is in future
        """
        today = datetime.date.today()
        if day>=today:
            raise serializers.ValidationError(_('Date sending cannot be post dated'))
        return day

    def validate(self, data):
        sub_branch = data['booth']
        branch = data['branch']
        reference = data['reference']
        exchange = data['exchange']
        if sub_branch and (not is_sub_branch_under_branch(sub_branch,branch)):
            raise serializers.ValidationError(_('Branch/ Sub-branch Mismatch'))
        try:
            validate_all_reference(exchange.name, reference)
        except Exception as e:
            raise serializers.ValidationError({'reference': e.message})
        if (data['cash_incentive_status'] != 'P') and (not data["unpaid_cash_incentive_reason"]):
            raise serializers.ValidationError({'unpaid_cash_incentive_reason': 'Reason is required if cash incentive status is unpaid'})
        return data

    @transaction.atomic
    def create(self, validated_data):
        remit = Remmit(**validated_data)
        remit._entry_cat = validated_data['cash_incentive_status']
        remit._reason_a = validated_data['unpaid_cash_incentive_reason']
        if remit._entry_cat=='P':
            remit.cash_incentive_amount= remit.calculate_cash_incentive()
            remit.date_cash_incentive_paid = timezone.now()
        else:
            remit.cash_incentive_amount= 0.00
        remit.save()
        return remit
                

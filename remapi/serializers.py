from django.db.models.query import QuerySet
from rest_framework import serializers
from django.contrib.auth.models import User
from rem.models import Receiver, Remmit, Country, ExchangeHouse, Branch, Booth
from schedules.models import Currency

class ReceiverSerializer(serializers.ModelSerializer):
    #nationality = serializers.SlugRelatedField(queryset=Country.objects.all(), slug_field ='name')

    class Meta:
        model=Receiver
        fields = ['name','gender','father_name','mother_name','spouse_name'
                    ,'ac_no','address','dob','cell','idtype','idissue','idexpire',
                    'idno', 'created_by']



class RemmitSerializer(serializers.ModelSerializer):
    exchange = serializers.SlugRelatedField(queryset=ExchangeHouse.objects.all(), slug_field ='name')
    rem_country = serializers.SlugRelatedField(queryset=Country.objects.all(), slug_field ='name')
    currency = serializers.SlugRelatedField(queryset=Currency.objects.all(), slug_field='short')
    receiver = serializers.HyperlinkedRelatedField(queryset=Receiver.objects.all(), view_name='receiver-detail')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='code')
    #image = serializers.CharField(max_length=100)
    sub_branch = serializers.SlugRelatedField(queryset=Booth.objects.all(), slug_field='code', source='booth')
    #created_by = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model=Remmit
        fields=['receiver','exchange','branch','sub_branch','rem_country','reference','sender','sender_occupation',
                'sender_gender','amount', 'currency','relationship', 'purpose', 'date_sending',
                'cash_incentive_status','unpaid_cash_incentive_reason', 'screenshot']

    def create(self, validated_data):
        remit = Remmit(**validated_data)
        remit._entry_cat = validated_data['cash_incentive_status']
        remit.save()
        return remit
                

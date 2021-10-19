from django.shortcuts import render
from rem.models import Receiver, Remmit, Requestpay, Payment
from rem.DataModels import get_client_ip
from rest_framework import viewsets
from rest_framework import permissions
from remapi.serializers import ReceiverSerializer, RemmitSerializer
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.


class ReceiverViewset(viewsets.ModelViewSet):
    queryset= Receiver.objects.all()
    serializer_class= ReceiverSerializer
    permission_classes = [permissions.IsAuthenticated]




class RemmitViewset(viewsets.ModelViewSet):
    queryset= Remmit.objects.all()
    serializer_class= RemmitSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        req = Requestpay(remittance=instance, created_by=self.request.user, status='PD', ip=get_client_ip(self.request))
        req.save()
        req.refresh_from_db()
        payment = Payment(requestpay=req, paid_by=self.request.user, agent_screenshot=serializer.data['screenshot'], ip=get_client_ip(self.request))
        payment.save()



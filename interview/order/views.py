from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from interview.order.models import Order, OrderTag
from interview.order.serializers import (
    OrderSerializer,
    OrderTagSerializer,
    OrderDeactivateSerializer,
)

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderTagListCreateView(generics.ListCreateAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer


class DeactivateOrderView(generics.UpdateAPIView):
    """
    API view to deactivate an order by setting its is_active field to False.
    """
    queryset = Order.objects.all()
    serializer_class = OrderDeactivateSerializer

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        order.is_active = False
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

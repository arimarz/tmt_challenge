from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_date

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
    
class OrderListByDateView(generics.ListAPIView):
    """
    API view to list orders between a specific start date and embargo date.
    """
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        start_date_str = self.request.query_params.get('start_date')
        embargo_date_str = self.request.query_params.get('embargo_date')

        if not start_date_str or not embargo_date_str:
            raise ValidationError({
                'error': 'Both "start_date" and "embargo_date" query parameters are required.'
            })

        start_date = parse_date(start_date_str)
        embargo_date = parse_date(embargo_date_str)

        if not start_date or not embargo_date:
            raise ValidationError({
                'error': 'Invalid date format. Use "YYYY-MM-DD".'
            })

        if start_date > embargo_date:
            raise ValidationError({
                'error': '"start_date" must be before or equal to "embargo_date".'
            })

        return queryset.filter(
            start_date__gte=start_date,
            embargo_date__lte=embargo_date
        )

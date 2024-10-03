from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from interview.order.models import Order, OrderTag
from interview.inventory.models import Inventory, InventoryType, InventoryLanguage
from django.utils import timezone
import datetime


class DeactivateOrderViewTest(TestCase):
    """Tests for the DeactivateOrderView."""

    def setUp(self):
        self.client = APIClient()
        # Create inventory dependencies
        self.inventory_type = InventoryType.objects.create(name='Type1')
        self.inventory_language = InventoryLanguage.objects.create(name='English')
        self.inventory = Inventory.objects.create(
            name='Inventory Item',
            type=self.inventory_type,
            language=self.inventory_language,
            metadata={}
        )
        # Create an order
        self.order = Order.objects.create(
            inventory=self.inventory,
            start_date=timezone.now().date(),
            embargo_date=(timezone.now() + datetime.timedelta(days=7)).date(),
            is_active=True
        )
        self.deactivate_url = reverse('order-deactivate', kwargs={'pk': self.order.pk})

    def test_deactivate_order_success(self):
        """Test deactivating an existing order."""
        response = self.client.patch(self.deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_active)

    def test_deactivate_nonexistent_order(self):
        """Test deactivating a non-existent order returns 404."""
        url = reverse('order-deactivate', kwargs={'pk': 9999})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class OrderListByDateViewTest(TestCase):
    """Tests for the OrderListByDateView."""

    def setUp(self):
        self.client = APIClient()
        # Create inventory dependencies
        self.inventory_type = InventoryType.objects.create(name='Type1')
        self.inventory_language = InventoryLanguage.objects.create(name='English')
        self.inventory = Inventory.objects.create(
            name='Inventory Item',
            type=self.inventory_type,
            language=self.inventory_language,
            metadata={}
        )

        # Create orders with different dates
        self.order1 = Order.objects.create(
            inventory=self.inventory,
            start_date=timezone.now().date(),
            embargo_date=(timezone.now() + datetime.timedelta(days=5)).date(),
            is_active=True
        )
        self.order2 = Order.objects.create(
            inventory=self.inventory,
            start_date=(timezone.now() + datetime.timedelta(days=6)).date(),
            embargo_date=(timezone.now() + datetime.timedelta(days=10)).date(),
            is_active=True
        )
        self.order3 = Order.objects.create(
            inventory=self.inventory,
            start_date=(timezone.now() + datetime.timedelta(days=11)).date(),
            embargo_date=(timezone.now() + datetime.timedelta(days=15)).date(),
            is_active=True
        )

        self.url = reverse('order-list-by-date')

    def test_list_orders_within_date_range(self):
        """Test listing orders within a specific date range."""
        start_date = (timezone.now() + datetime.timedelta(days=1)).date().isoformat()
        embargo_date = (timezone.now() + datetime.timedelta(days=12)).date().isoformat()
        response = self.client.get(self.url, {
            'start_date': start_date,
            'embargo_date': embargo_date
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        returned_ids = [order['id'] for order in response.data]
        self.assertIn(self.order2.id, returned_ids)
        self.assertIn(self.order3.id, returned_ids)

    def test_missing_query_parameters(self):
        """Test that both query parameters are required."""
        response = self.client.get(self.url, {
            'start_date': '2023-01-01'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_invalid_date_format(self):
        """Test that invalid date formats return an error."""
        response = self.client.get(self.url, {
            'start_date': 'invalid-date',
            'embargo_date': '2023-01-10'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_start_date_after_embargo_date(self):
        """Test that start_date after embargo_date returns an error."""
        response = self.client.get(self.url, {
            'start_date': '2023-01-10',
            'embargo_date': '2023-01-01'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
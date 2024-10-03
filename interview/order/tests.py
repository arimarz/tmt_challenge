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
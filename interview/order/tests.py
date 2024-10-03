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

class OrderTagsListViewTest(TestCase):
    """Tests for the OrderTagsListView."""

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

        # Create order tags
        self.tag1 = OrderTag.objects.create(name='Tag1', is_active=True)
        self.tag2 = OrderTag.objects.create(name='Tag2', is_active=True)
        self.tag3 = OrderTag.objects.create(name='Tag3', is_active=True)

        # Create an order and associate tags
        self.order = Order.objects.create(
            inventory=self.inventory,
            start_date=timezone.now().date(),
            embargo_date=(timezone.now() + datetime.timedelta(days=5)).date(),
            is_active=True
        )
        self.order.tags.add(self.tag1, self.tag2)

        self.url = reverse('order-tags', kwargs={'pk': self.order.pk})

    def test_list_tags_associated_with_order(self):
        """Test listing tags associated with an order."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        tag_names = [tag['name'] for tag in response.data]
        self.assertIn(self.tag1.name, tag_names)
        self.assertIn(self.tag2.name, tag_names)

    def test_order_not_found(self):
        """Test that a 404 is returned if the order does not exist."""
        url = reverse('order-tags', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Order not found.')

class OrdersByTagViewTest(TestCase):
    """Tests for the OrdersByTagView."""

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

        # Create order tags
        self.tag1 = OrderTag.objects.create(name='Tag1', is_active=True)
        self.tag2 = OrderTag.objects.create(name='Tag2', is_active=True)

        # Create orders and associate tags
        self.order1 = Order.objects.create(
            inventory=self.inventory,
            start_date=timezone.now().date(),
            embargo_date=(timezone.now() + datetime.timedelta(days=5)).date(),
            is_active=True
        )
        self.order1.tags.add(self.tag1)

        self.order2 = Order.objects.create(
            inventory=self.inventory,
            start_date=timezone.now().date(),
            embargo_date=(timezone.now() + datetime.timedelta(days=10)).date(),
            is_active=True
        )
        self.order2.tags.add(self.tag1, self.tag2)

        self.url = reverse('orders-by-tag', kwargs={'tag_id': self.tag1.id})

    def test_list_orders_associated_with_tag(self):
        """Test listing orders associated with a tag."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        order_ids = [order['id'] for order in response.data]
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order2.id, order_ids)

    def test_tag_not_found(self):
        """Test that a 404 is returned if the tag does not exist."""
        url = reverse('orders-by-tag', kwargs={'tag_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Tag not found.')
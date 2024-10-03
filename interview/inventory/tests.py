from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from interview.inventory.models import Inventory, InventoryType, InventoryLanguage
from django.utils import timezone
import datetime

class InventoryListAfterDateViewTest(APITestCase):
    def setUp(self):
        # Create necessary foreign key objects
        self.inventory_type = InventoryType.objects.create(name='Type1')
        self.inventory_language = InventoryLanguage.objects.create(name='English')

        # Create inventory items with different creation dates
        self.inventory1 = Inventory.objects.create(
            name='Item 1',
            type=self.inventory_type,
            language=self.inventory_language,
            metadata={},
            created_at=timezone.now() - datetime.timedelta(days=5)
        )
        self.inventory2 = Inventory.objects.create(
            name='Item 2',
            type=self.inventory_type,
            language=self.inventory_language,
            metadata={},
            created_at=timezone.now() - datetime.timedelta(days=3)
        )
        self.inventory3 = Inventory.objects.create(
            name='Item 3',
            type=self.inventory_type,
            language=self.inventory_language,
            metadata={},
            created_at=timezone.now()
        )

    def test_missing_created_after_parameter(self):
        url = reverse('inventory-created-after')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'The "created_after" query parameter is required.')

    def test_invalid_created_after_format(self):
        url = reverse('inventory-created-after')
        response = self.client.get(url, {'created_after': 'invalid-date'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid date format for "created_after". Use YYYY-MM-DD.')

    def test_inventory_list_after_valid_date(self):
        url = reverse('inventory-created-after')
        created_after = (timezone.now() - datetime.timedelta(days=4)).date().isoformat()
        response = self.client.get(url, {'created_after': created_after})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        returned_ids = [item['id'] for item in response.data]
        self.assertIn(self.inventory2.id, returned_ids)
        self.assertIn(self.inventory3.id, returned_ids)

class InventoryListPaginationTest(APITestCase):
    def setUp(self):
        # Create necessary foreign key objects
        self.inventory_type = InventoryType.objects.create(name='Type1')
        self.inventory_language = InventoryLanguage.objects.create(name='English')

        # Create multiple inventory items for pagination testing
        for i in range(10):
            Inventory.objects.create(
                name=f'Item {i+1}',
                type=self.inventory_type,
                language=self.inventory_language,
                metadata={},
                created_at=timezone.now() - datetime.timedelta(days=i)
            )

    def test_default_pagination_limit(self):
        """
        Ensure the default pagination limit is 3 items per page.
        """
        url = reverse('inventory-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['count'], 10)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_custom_limit_and_offset(self):
        """
        Ensure pagination works with custom limit and offset parameters.
        """
        url = reverse('inventory-list')
        response = self.client.get(url, {'limit': 5, 'offset': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        item_names = [item['name'] for item in response.data['results']]
        expected_names = ['Item 5', 'Item 4', 'Item 3', 'Item 2', 'Item 1']
        self.assertEqual(item_names, expected_names)
from django.test import TestCase, Client
from unittest.mock import patch
from django.urls import reverse
from .models import Order
from .forms import OrderUpdateForm, OrderFilterForm
from . import views
from decimal import Decimal, InvalidOperation
import json

class OrderViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.order1 = Order.objects.create(
            table_number=1,
            items=[{'name': 'Burger', 'price': '10.99'}],
            total_price=Decimal('10.99'),
            status='pending'
        )
        self.order2 = Order.objects.create(
            table_number=2,
            items=[{'name': 'Pizza', 'price': '12.00'}],
            total_price=Decimal('12.00'),
            status='paid'
        )
        self.list_url = reverse('orders_list')
        self.create_url = reverse('order_create')
        self.update_url = reverse('order_edit', args=[self.order1.pk])
        self.delete_url = reverse('order_delete', args=[self.order1.pk])

    def test_order_list_view_get(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/orders_list.html')
        self.assertContains(response, 'Burger')  # Check if order details are present
        self.assertContains(response, 'Pizza')
        self.assertContains(response, '12.00') # Test revenue displayed.
        self.assertIsInstance(response.context['form'], OrderFilterForm)
        self.assertEqual(len(response.context['orders']), 2) # all orders

    def test_order_list_view_filter_status(self):
        response = self.client.get(self.list_url, {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 1) # Check filtering.
        self.assertEqual(response.context['orders'][0].status, 'pending')

    def test_order_list_view_filter_table(self):
        response = self.client.get(self.list_url, {'table_number': 2})
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0].table_number, 2)

    def test_order_list_view_filter_search(self):
        response = self.client.get(self.list_url, {'search': 'Bur'})
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0].items[0]['name'], 'Burger')

    def test_order_list_view_filter_ordering(self):
      response = self.client.get(self.list_url, {'ordering': 'total_price'})
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context['orders']), 2)
      self.assertEqual(response.context['orders'][0].total_price, Decimal('10.99')) # Check ordering (ascending).
      self.assertEqual(response.context['orders'][1].total_price, Decimal('12.00'))

    def test_order_list_view_exception(self):
        # Simulate an error (e.g. by mocking Order.objects.all to raise an exception).
        with patch('orders.models.Order.objects.all', side_effect=Exception("Test Exception")):
          response = self.client.get(self.list_url)
          self.assertEqual(response.status_code, 500)
          self.assertEqual(response.content.decode(), "An error occurred while processing your request.")

    def test_order_create_view_get(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_form.html')

    def test_order_create_view_post_valid(self):
        data = {'table_number': 3, 'items': 'Pasta 8.50, Juice 2.00'}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertEqual(Order.objects.count(), 3)  # Check if order was created
        new_order = Order.objects.get(table_number=3)
        self.assertEqual(new_order.total_price, Decimal('10.50'))
        self.assertEqual(new_order.status, 'pending')
        self.assertEqual(new_order.items, [{'name': 'Pasta', 'price': '8.50'}, {'name': 'Juice', 'price': '2.00'}])

    def test_order_create_view_post_missing_fields(self):
        data = {'table_number': 3}  # Missing items
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 400)

        data = {'items': 'Pasta 8.50'}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 2) # No new orders.


    def test_order_update_view_get(self):
      response = self.client.get(self.update_url)
      self.assertEqual(response.status_code, 200)
      self.assertTemplateUsed(response, 'orders/order_edit.html')
      self.assertIsInstance(response.context['form'], OrderUpdateForm)
      self.assertEqual(response.context['order'].pk, self.order1.pk)

    def test_order_update_view_post_invalid(self):
        data = {'table_number': 'abc', 'items': 'Invalid Item', 'status': 'invalid'}
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertTemplateUsed(response, 'orders/order_edit.html') # with errors
        self.assertFalse(response.context['form'].is_valid()) # form has errors

    def test_order_update_view_not_found(self):
        invalid_update_url = reverse('order_edit', args=[999]) # Non-existent ID
        response = self.client.get(invalid_update_url)
        self.assertEqual(response.status_code, 404)


    def test_order_delete_view_get(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_confirm_delete.html')
        self.assertEqual(response.context['order'].pk, self.order1.pk)


    def test_order_delete_view_post(self):
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Order.objects.count(), 1)  # Check if order was deleted

    def test_order_delete_view_not_found(self):
        invalid_delete_url = reverse('order_delete', args=[999])
        response = self.client.get(invalid_delete_url)
        self.assertEqual(response.status_code, 404)

    def test_order_delete_view_exception(self):
      from unittest.mock import patch
      with patch('orders.models.Order.delete', side_effect=Exception("Test exception")):
          response = self.client.post(self.delete_url)
          self.assertEqual(response.status_code, 500)

    def test_parse_items_valid(self):
        items_input = "Burger 10.99, Fries 3.99, Coke 2.50"
        expected_items = [
            {'name': 'Burger', 'price': '10.99'},
            {'name': 'Fries', 'price': '3.99'},
            {'name': 'Coke', 'price': '2.50'}
        ]
        result = views.parse_items(items_input)
        self.assertEqual(result, expected_items)

        items_input = "  Burger   10.99  ,  Fries   3.99   " # extra spaces
        expected_items = [
            {'name': 'Burger', 'price': '10.99'},
            {'name': 'Fries', 'price': '3.99'}
        ]
        result = views.parse_items(items_input)
        self.assertEqual(result, expected_items)

        items_input = "Large   Burger  with extra cheese   15.99"  # name with spaces
        expected_items = [
             {'name': 'Large Burger with extra cheese', 'price': '15.99'}
        ]
        self.assertEqual(views.parse_items(items_input), expected_items)


    def test_parse_items_invalid(self):
        items_input = "Burger, Fries 3.99"  # Missing price
        with self.assertRaises(ValueError) as context:
            views.parse_items(items_input)
        self.assertTrue('Invalid item format' in str(context.exception))

        items_input = "Burger ten, Fries 3.99"  # Invalid price
        with self.assertRaises(InvalidOperation) as context:
            views.parse_items(items_input)

        items_input = "Burger 10, Fries" # Invalid item
        with self.assertRaises(ValueError) as context:
             views.parse_items(items_input)
        self.assertTrue('Invalid item format' in str(context.exception))

    def test_parse_items_mixed(self): # valid and invalid
        items_input = "Burger 10.99, Fries, Coke 2.50, Pizza"
        expected = [{'name': 'Burger', 'price': '10.99'}, {'name': 'Coke', 'price': '2.50'}]

        with self.assertRaises(ValueError) as context:
            views.parse_items(items_input)


class OrderSerializerTest(TestCase):
    def test_serializer_valid(self):
        from .serializers import OrderSerializer
        data = {
            'table_number': 1,
            'items': [{'name': 'Burger', 'price': '10.99'}],
            'total_price': '10.99',
            'status': 'pending',
        }
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid(self):
        from .serializers import OrderSerializer
        data = {
            'table_number': 'abc',  # Invalid table number
            'items': 'invalid',  # Invalid items
            'total_price': 'abc',  # Invalid total_price
            'status': 'invalid_status',  # Invalid status
        }
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())

class OrderFilterFormTest(TestCase):
    def test_valid_filter_form(self):
        data = {'status': 'pending', 'table_number': 1, 'search': 'Burger', 'ordering': 'total_price'}
        form = OrderFilterForm(data=data)
        self.assertTrue(form.is_valid())

    def test_empty_filter_form(self):
        form = OrderFilterForm(data={})
        self.assertTrue(form.is_valid())  # All fields are optional

class OrderUpdateFormTest(TestCase):
    def test_invalid_form(self):
        data = {
            'table_number': 'abc',  # Invalid table number
            'items': "Burger ten",
            'status': 'invalid_status',  # Invalid status
        }
        form = OrderUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('table_number', form.errors)
        self.assertIn('status', form.errors)
        self.assertIn('items', form.errors)
        self.assertFalse(OrderUpdateForm(data={'table_number': 1, 'items': 'abc', 'status': 'ready'}).is_valid()) # invalid item

class OrderModelTest(TestCase):
    def test_order_creation(self):
        order = Order.objects.create(
            table_number=1,
            items=[{'name': 'Burger', 'price': '10.99'}],
            total_price=Decimal('14.98'),
            status='pending'
        )
        self.assertEqual(order.table_number, 1)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.total_price, Decimal('14.98'))
        self.assertEqual(order.status, 'pending')
        self.assertEqual(str(order), "Заказ {} | Стол 1 | В ожидании".format(order.id))

    def test_status_choices(self):
        order = Order.objects.create(
            table_number=1,
            items=[{'name': 'Burger', 'price': '10.99'}],
            total_price=Decimal('10.99'),
            status='pending'
        )
        self.assertEqual(order.get_status_display(), 'В ожидании')

        order.status = 'ready'
        order.save()
        self.assertEqual(order.get_status_display(), 'Готово')

        order.status = 'paid'
        order.save()
        self.assertEqual(order.get_status_display(), 'Оплачено')

    def test_default_status(self):
        order = Order.objects.create(
            table_number = 2,
            items = [{'name': 'Pizza', 'price': '12.00'}],
            total_price = Decimal('12.00')
        )
        self.assertEqual(order.status, 'pending') # Check default status.

    def test_total_price_calculation(self):
        order = Order(
            table_number=3,
            items=[{'name': 'Salad', 'price': '7.50'}, {'name': 'Soup', 'price': '5.00'}]
        )
        # Manually calculate expected total price since it is a required field.
        expected_total_price = Decimal('7.50') + Decimal('5.00')
        order.total_price = expected_total_price  # Set the total_price before saving.
        order.save()  # Now save should work.
        self.assertEqual(order.total_price, expected_total_price)
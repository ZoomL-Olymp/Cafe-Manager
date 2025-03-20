from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect
from django.http import Http404
from .models import Order
from .serializers import OrderSerializer
from decimal import Decimal
import json

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer

    # Фильтрация и поиск
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'table_number']
    search_fields = ['items']
    ordering_fields = ['total_price', 'created_at']

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'orders/orders_list.html', {'orders': orders})

def order_create(request):
    if request.method == 'POST':
        table_number = request.POST.get('table_number')
        items_input = request.POST.get('items')
        items = parse_items(items_input)  # Функция для парсинга строкового ввода в список блюд
        total_price = sum(int(item['price']) for item in items)
        
        order = Order.objects.create(
            table_number=table_number,
            items=items,
            total_price=Decimal(total_price),
            status='pending'
        )
        return redirect('orders_list')
    
    return render(request, 'orders/order_form.html')

def order_update_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Заказ не найден.")
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        return redirect('orders_list')
    
    return redirect('orders_list')

def parse_items(items_input):
    """Парсит строку ввода в список блюд с ценами, преобразует цену в строку"""
    items = []
    for item_str in items_input.split(','):
        name, price = item_str.strip().split(' ')
        items.append({'name': name, 'price': str(Decimal(price))})  # Преобразование в строку
    return items
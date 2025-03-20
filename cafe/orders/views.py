from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.db.models import Sum
from .models import Order
from .forms import OrderUpdateForm, OrderFilterForm
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
    revenue = Order.objects.filter(status='paid').aggregate(total=Sum('total_price'))['total'] or 0
    form = OrderFilterForm(request.GET)

    if form.is_valid():
        status = form.cleaned_data.get('status')
        table_number = form.cleaned_data.get('table_number')
        search = form.cleaned_data.get('search')
        ordering = form.cleaned_data.get('ordering')

        if status:
            orders = orders.filter(status=status)
        if table_number:
            orders = orders.filter(table_number=table_number)
        if search:
            orders = orders.filter(Q(items__contains=search))
        if ordering:
            orders = orders.order_by(ordering)

    return render(request, 'orders/orders_list.html', {'orders': orders, 'revenue': revenue, 'form': form})

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

def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders_list')
    else:
        form = OrderUpdateForm(instance=order)  # Загружаем текущие данные

    return render(request, 'orders/order_edit.html', {'form': form, 'order': order})

def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('orders_list')
    return render(request, 'orders/order_confirm_delete.html', {'order': order})

def parse_items(items_input):
    """Парсит строку ввода в список блюд с ценами, преобразует цену в строку"""
    items = []
    for item_str in items_input.split(','):
        name, price = item_str.strip().split(' ')
        items.append({'name': name, 'price': str(Decimal(price))})  # Преобразование в строку
    return items

def daily_revenue(request):
    revenue = Order.objects.filter(status='paid').aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'orders/revenue.html', {'revenue': revenue})
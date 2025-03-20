from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer

    # Фильтрация и поиск
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'table_number']
    search_fields = ['items']
    ordering_fields = ['total_price', 'created_at']

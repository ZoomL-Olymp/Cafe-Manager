from django import forms
from .models import Order

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number', 'items', 'status']  # Разрешаем изменять всё нужное
        labels = {
            'table_number': 'Номер стола',
            'items': 'Список блюд',
            'status': 'Статус заказа'
        }
        widgets = {
            'items': forms.Textarea(attrs={'rows': 3})  # Чтобы удобнее вводить список блюд
        }
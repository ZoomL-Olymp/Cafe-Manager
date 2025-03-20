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

class OrderFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Все'),
        ('pending', 'В ожидании'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено'),
    ]
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label="Статус заказа")
    table_number = forms.IntegerField(required=False, label="Номер стола")
    search = forms.CharField(max_length=100, required=False, label="Поиск по блюдам")
    ordering = forms.ChoiceField(
        choices=[('', 'Без сортировки'), ('total_price', 'Цена'), ('created_at', 'Дата создания')],
        required=False, label="Сортировка"
    )
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseBadRequest, HttpResponseServerError
from django.db.models import Sum, Q  # Import Q for complex queries
from .models import Order
from .forms import OrderUpdateForm, OrderFilterForm
from .serializers import OrderSerializer
from decimal import Decimal
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer

    # Фильтрация и поиск
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'table_number']
    search_fields = ['items']  #  search by item name
    ordering_fields = ['total_price', 'created_at']



def order_list(request):
    try:
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
                orders = orders.filter(items__icontains=search) # Use icontains for case-insensitive search
            if ordering:
                orders = orders.order_by(ordering)

        return render(request, 'orders/orders_list.html', {'orders': orders, 'revenue': revenue, 'form': form})
    except Exception as e:
        #  Log the exception for debugging
        print(f"Error in order_list: {e}")
        return HttpResponseServerError("An error occurred while processing your request.")

# @method_decorator(csrf_exempt, name='dispatch') #  for POST without CSRF
def order_create(request):
    if request.method == 'POST':
        try:
            table_number = request.POST.get('table_number')
            items_input = request.POST.get('items')

            if not table_number or not items_input:
                return HttpResponseBadRequest("Table number and items are required.")

            items = parse_items(items_input)
            if not items:  # Check if items were parsed correctly
               return HttpResponseBadRequest("Invalid items format.")
            total_price = sum(Decimal(item['price']) for item in items)

            order = Order.objects.create(
                table_number=table_number,
                items=items,
                total_price=total_price,
                status='pending'
            )
            return redirect('orders_list')
        except (ValueError, KeyError) as e:
            # Handle specific errors during parsing or creation
            return HttpResponseBadRequest(f"Invalid input data: {e}")
        except Exception as e:
            print(f"Error in order_create: {e}")
            return HttpResponseServerError("An error occurred while creating the order.")

    return render(request, 'orders/order_form.html')


def order_update(request, pk):
    try:
        order = get_object_or_404(Order, pk=pk)

        if request.method == 'POST':
            form = OrderUpdateForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect('orders_list')
            else:
                return render(request, 'orders/order_edit.html', {'form': form, 'order': order}) #return form with errors
        else:
            form = OrderUpdateForm(instance=order)
        return render(request, 'orders/order_edit.html', {'form': form, 'order': order})

    except Http404:
        raise Http404("Order not found")  #  explicitly raise 404
    except Exception as e:
        print(f"Error in order_update: {e}")
        return HttpResponseServerError("An error occurred while updating the order.")



def order_delete(request, pk):
    try:
        order = get_object_or_404(Order, pk=pk)
        if request.method == 'POST':
            order.delete()
            return redirect('orders_list')
        return render(request, 'orders/order_confirm_delete.html', {'order': order})
    except Http404:
        raise Http404("Order not found")
    except Exception as e:
        print(f"Error in order_delete: {e}")
        return HttpResponseServerError("An error occurred while deleting the order.")

def parse_items(items_input):
    """Parses the input string into a list of dishes with prices, converts the price to a string."""
    items = []
    try:
        for item_str in items_input.split(','):
            parts = item_str.strip().split()
            if len(parts) < 2: # Check we have at least name and price
                raise ValueError(f"Invalid item format: {item_str}")

            name = " ".join(parts[:-1])  # Join all parts except the last one as the name
            price = parts[-1]  # The last part is the price

            try:
                Decimal(price) # Test if price is valid
            except (ValueError, TypeError):
                raise ValueError(f"Invalid price format: {price}")

            items.append({'name': name, 'price': str(price)})
    except ValueError as e:
        print(f"Error parsing items: {e}")
        return [] # Return empty if error
    return items
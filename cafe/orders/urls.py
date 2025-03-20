from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views


router = DefaultRouter()
router.register(r'orders', views.OrderViewSet)  # API /api/orders/

# API
urlpatterns = [
    path('api/', include(router.urls)),
]

# API docs
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# CRUD
urlpatterns += [
    path('', views.order_list, name='orders_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:pk>/edit/', views.order_update, name='order_edit'), 
    path('<int:pk>/delete/', views.order_delete, name='order_delete'),
]
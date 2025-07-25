from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'order', views.OrderViewSet, basename='order')
router.register(r'order-detail', views.OrderDetailViewSet, basename='order-detail')

urlpatterns = [
    path('', include(router.urls)),
]
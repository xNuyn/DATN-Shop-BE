from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'compare-product', views.CompareProductViewSet, basename='compare-product')

urlpatterns = [
    path('', include(router.urls)),
]


from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]


from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('upload/', UploadImageView.as_view(), name='upload-image'),
    path('', include('users.urls')),
    path('', include('discounts.urls')),
    path('', include('products.urls')),
    path('', include('cart.urls')),
    path('', include('compare.urls')),
    path('', include('orders.urls')),
    path('', include('payments.urls')),
    path('', include('reviews.urls')),
    path('', include('shipping.urls')),
    path('', include('chat_app.urls')),
    path('', include('admin.urls')),
]

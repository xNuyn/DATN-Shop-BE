from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from app.views import UploadImageView

router = DefaultRouter()
router.register(r'', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]


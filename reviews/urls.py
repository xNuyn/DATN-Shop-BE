from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'review', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]

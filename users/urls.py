from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from app.views import UploadImageView

router = DefaultRouter()
router.register(r'', views.UserViewSet, basename='user')

urlpatterns = [
    path('search-and', views.UserSearchView.as_view(), name='user-search-and'),
    path('search-or', views.UserSearchViewOR.as_view(), name='user-search-or'),
    path('', include(router.urls)),
]


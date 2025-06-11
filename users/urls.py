from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    path('search-and', views.UserSearchView.as_view(), name='user-search-and'),
    path('search-or', views.UserSearchViewOR.as_view(), name='user-search-or'),
    path('', include(router.urls)),
]


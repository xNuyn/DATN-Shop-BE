from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Website API",
      default_version='v1',
      description="API cho hệ thống",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="tranxuannguyen732@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes= (),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    
    # Swagger routes
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
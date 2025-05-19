from django.db import models
from app.models import StatusEnum

class User(models.Model):
    CUSTOMER = "customer"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (CUSTOMER, "Customer"),
        (ADMIN, "Admin"),
    ]

    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, unique=True, null=False)
    full_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=255, unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    refresh_token = models.CharField(max_length=255, null= True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    address_billing = models.TextField(null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)
    
    def __str__(self):
        return self.user_name
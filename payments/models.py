import uuid
from django.db import models
from orders.models import Order
from app.models import StatusEnum

# ---------------- PAYMENT METHOD ---------------- #
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)

    def __str__(self):
        return self.name


# ---------------- PAYMENTS ---------------- #
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name="payments")
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"Payment {self.id} - Order {self.order.id} - {self.status}"

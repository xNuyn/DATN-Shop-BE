from django.db import models
from orders.models import Order
from app.models import StatusEnum

# ---------------- SHIPMENT ---------------- #
class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
    tracking_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    estimate_delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)  # Thời gian giao hàng thành công
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"Shipment {self.id} - {self.status}"

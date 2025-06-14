from django.db import models
from users.models import User
from products.models import SubProduct
from app.models import StatusEnum
# ---------------- ORDERS ---------------- #
class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    subtotal = models.DecimalField(max_digits=20, decimal_places=2)
    total_price = models.DecimalField(max_digits=20, decimal_places=2)
    tax = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"

# ---------------- ORDER DETAILS ---------------- #
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_details")
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, related_name="order_details")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"Order {self.order.id} - {self.sub_product.product.name} - Qty: {self.quantity}"

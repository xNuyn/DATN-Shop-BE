from django.db import models
from users.models import User
from products.models import SubProduct

# ---------------- CART ---------------- #
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, related_name="cart_entries")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'sub_product')  # Tránh trùng lặp sản phẩm trong giỏ hàng

    def __str__(self):
        return f"{self.user.user_name} - {self.sub_product.id} ({self.quantity})"


# ---------------- WISHLIST ---------------- #
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, related_name="wishlist_entries")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'sub_product')  # Tránh trùng lặp sản phẩm trong wishlist

    def __str__(self):
        return f"{self.user.user_name} - {self.sub_product.id}"

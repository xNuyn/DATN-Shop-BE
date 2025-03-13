from django.db import models
from users.models import User
from products.models import SubProduct
from django.core.validators import MinValueValidator, MaxValueValidator

# ---------------- REVIEWS ---------------- #
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} - {self.sub_product.product.name} - {self.rating}⭐"

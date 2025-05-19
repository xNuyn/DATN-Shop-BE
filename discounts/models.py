from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from app.models import StatusEnum

# ---------------- COUPON ---------------- #
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, null=False)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)]
    )
    quantity = models.PositiveIntegerField()
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

    def is_valid(self):
        """Kiểm tra xem mã giảm giá có hợp lệ không"""
        from django.utils.timezone import now
        return self.is_active and self.valid_from <= now().date() <= self.valid_until

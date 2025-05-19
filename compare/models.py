from django.db import models
from users.models import User
from products.models import SubProduct
from app.models import StatusEnum

# ---------------- COMPARE PRODUCT ---------------- #
class CompareProduct(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    sub_product = models.ForeignKey("products.SubProduct", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices,default=StatusEnum.ACTIVE)

    class Meta:
        unique_together = ("user", "sub_product") 

    def __str__(self):
        return f"{self.user.email} compares {self.sub_product.id}"

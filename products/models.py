from django.db import models

# ---------------- CATEGORIES ---------------- #
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name="subcategories"
    )

    def __str__(self):
        return self.name

# ---------------- BRANDS ---------------- #
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

# ---------------- PRODUCTS ---------------- #
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

# ---------------- SUBPRODUCTS ---------------- #
class SubProduct(models.Model):
    class ColorChoices(models.TextChoices):
        RED = "Red"
        BLUE = "Blue"
        GREEN = "Green"
        BLACK = "Black"
        WHITE = "White"

    class SizeChoices(models.TextChoices):
        SMALL = "S"
        MEDIUM = "M"
        LARGE = "L"
        XLARGE = "XL"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="subproducts")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=10, choices=ColorChoices.choices)
    size = models.CharField(max_length=5, choices=SizeChoices.choices)
    stock = models.PositiveIntegerField(default=0)
    image = models.TextField(null=True, blank=True)
    specification = models.TextField(null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"

# ---------------- PRODUCT - SUBPRODUCT RELATION ---------------- #
class ProductSubProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("product", "sub_product")

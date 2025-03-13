from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]

    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, unique=True, null=False)
    full_name = models.CharField(max_length=100, null=False)
    image = models.TextField(null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    address_billing = models.TextField(null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"  # Tên bảng trong MySQL

    def __str__(self):
        return self.user_name
    
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.name
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)  # Cần định nghĩa Brand model
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = "brands"

    def __str__(self):
        return self.name

class SubProduct(models.Model):
    COLOR_CHOICES = [
        # ('red', 'Red'),
        # ('blue', 'Blue'),
        # ('green', 'Green'),
        # ('black', 'Black'),
    ]
    
    SIZE_CHOICES = [
        # ('S', 'Small'),
        # ('M', 'Medium'),
        # ('L', 'Large'),
        # ('XL', 'Extra Large'),
    ]

    old_price = models.BigIntegerField(null=True, blank=True)
    price = models.BigIntegerField(null=False)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, null=False)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, null=False)
    stock = models.IntegerField(default=0, null=False)
    image = models.TextField(null=True, blank=True)
    specification = models.TextField(null=False)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = "subproducts"

    def __str__(self):
        return f"SubProduct {self.id} - {self.color} {self.size}"
    
class ProductSubProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE)

    class Meta:
        db_table = "product_subproducts"
        unique_together = ('product', 'sub_product')

    def __str__(self):
        return f"Product {self.product.id} - SubProduct {self.sub_product.id}"
    
class Order(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (COMPLETED, 'Completed'),
        (CANCELED, 'Canceled'),
    ]

    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    subtotal = models.BigIntegerField()
    total_price = models.BigIntegerField()
    tax = models.BigIntegerField()
    discount = models.BigIntegerField()
    shipping_cost = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
        
    def __str__(self):
        return f"Order #{self.id} - {self.status}"

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sub_product = models.ForeignKey('SubProduct', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_details'
        
    def __str__(self):
        return f"OrderDetail (Order #{self.order.id} - {self.sub_product})"
    
class Reviews(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    sub_product = models.ForeignKey('SubProduct', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
    
    def __str__(self):
        return f"Review by User {self.user.id} - Rating: {self.rating}"
    
class Payment(models.Model):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (FAILED, 'Failed'),
    ]

    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
    
    def __str__(self):
        return f"Payment {self.id} - {self.status}"
    
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments_method'
    
    def __str__(self):
        return self.name
    
class Shipment(models.Model):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    IN_TRANSIT = 'in_transit'
    OUT_FOR_DELIVERY = 'out_for_delivery'
    DELIVERED = 'delivered'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SHIPPED, 'Shipped'),
        (IN_TRANSIT, 'In Transit'),
        (OUT_FOR_DELIVERY, 'Out for Delivery'),
        (DELIVERED, 'Delivered'),
    ]

    order = models.ForeignKey('Orders', on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=50, unique=True)
    estimate_delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipments'
    
    def __str__(self):
        return f"Shipment {self.id} - {self.status}"
    
class Wishlist(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    sub_product = models.ForeignKey('SubProducts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlists'
    
    def __str__(self):
        return f"Wishlist Item {self.id} - User {self.user.id}"
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.IntegerField()
    valid_from = models.DateField()
    valid_until = models.DateField()

    class Meta:
        db_table = 'coupons'
    
    def __str__(self):
        return f"Coupon {self.code} - {self.discount_percentage}% Off"
    
class Cart(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    sub_product = models.ForeignKey('SubProducts', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart {self.id} - User {self.user.id}"

class CompareProduct(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    sub_product = models.ForeignKey('SubProducts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compare_products'

    def __str__(self):
        return f"Compare Product {self.id} - User {self.user.id}"
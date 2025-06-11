import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
import csv
from django.db import transaction

# --------------------------------------------
# 1. Thiết lập môi trường Django
# --------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")  # <-- Thay your_project bằng tên project của bạn
django.setup()

# --------------------------------------------
# 2. Import tất cả các model cần thiết
# --------------------------------------------
from users.models import User  # model User của bạn
from products.models import Category, Brand, Product, SubProduct, ProductSubProduct
from reviews.models import Review
from cart.models import Cart, Wishlist
from orders.models import Order, OrderDetail
from compare.models import CompareProduct
from shipping.models import Shipping
from payments.models import PaymentMethod, Payment
from discounts.models import Coupon

from app.models import StatusEnum  # Enum trạng thái (ACTIVE/INACTIVE)

# --------------------------------------------
# 3. Hàm hỗ trợ: random tên, random màu, random size
# --------------------------------------------
COLOR_CHOICES = ["Red", "Blue", "Green", "Black", "White", "Yellow", "Purple", "Orange"]
SIZE_CHOICES = ["S", "M", "L", "XL", "XXL"]

def random_color():
    return random.choice(COLOR_CHOICES)

def random_size():
    return random.choice(SIZE_CHOICES)

def random_username(first, last):
    return (first[0] + last + str(random.randint(100, 999))).lower()

def random_password():
    return "password123"  # ví dụ đơn giản; bạn có thể hash sau khi import

# --------------------------------------------
# 4. Seed Category, Material, Brand
# --------------------------------------------
def seed_categories_materials_brands():
    print("→ Bắt đầu seed Category, Material, Brand …")

    # 4.1. Categories phân cấp 2–3 cấp (ví dụ)
    # Xoá hết trước (nếu bạn muốn reset). Cẩn thận khi chạy trên production!
    Category.objects.all().delete()

    # Tạo Categories cấp 1
    cat_root_names = ["Electronics", "Men Clothing", "Women Clothing", "Home & Living", "Sports"]
    root_cats = []
    for name in cat_root_names:
        c, _ = Category.objects.get_or_create(name=name, defaults={"description": f"{name} parent"})
        root_cats.append(c)

    # Tạo Category cấp 2 dưới mỗi root
    subcats = [
        ("Electronics", "Smartphones"),
        ("Electronics", "Tablets"),
        ("Electronics", "Laptops"),
        ("Men Clothing", "Shirts"),
        ("Men Clothing", "Pants"),
        ("Women Clothing", "Dresses"),
        ("Women Clothing", "Skirts"),
        ("Home & Living", "Furniture"),
        ("Home & Living", "Kitchen"),
        ("Sports", "Running"),
        ("Sports", "Fitness"),
    ]
    cat_map = {c.name: c for c in root_cats}

    second_level = []
    for parent_name, child_name in subcats:
        parent = cat_map[parent_name]
        c, _ = Category.objects.get_or_create(
            name=child_name,
            defaults={"description": f"{child_name} under {parent_name}", "parent": parent}
        )
        second_level.append(c)

    # Tạo Category cấp 3 (mỗi cấp 2 có 1–2 con cấp 3)
    third_level_info = {
        "Smartphones": ["Android Phones", "iOS Phones"],
        "Tablets": ["Android Tablets", "iPad"],
        "Laptops": ["Gaming Laptops", "Ultrabooks"],
        "Shirts": ["Casual Shirts", "Formal Shirts"],
        "Pants": ["Jeans", "Chinos"],
        "Dresses": ["Casual Dresses", "Evening Gowns"],
        "Skirts": ["Mini Skirts", "Maxi Skirts"],
        "Furniture": ["Sofas", "Tables"],
        "Kitchen": ["Cookware", "Utensils"],
        "Running": ["Running Shoes", "Running Apparel"],
        "Fitness": ["Yoga Mats", "Dumbbells"],
    }
    for parent_cat in second_level:
        names = third_level_info.get(parent_cat.name, [])
        for name in names:
            Category.objects.get_or_create(
                name=name,
                defaults={"description": f"{name} under {parent_cat.name}", "parent": parent_cat}
            )

    print(f"   Đã seed {Category.objects.count()} Categories.")

    # 4.2. Materials
    Material.objects.all().delete()
    material_names = ["Cotton", "Denim", "Leather", "Polyester", "Wool", "Silk", "Nylon"]
    for name in material_names:
        Material.objects.create(name=name, description=f"Material: {name}")
    print(f"   Đã seed {Material.objects.count()} Materials.")

    # 4.3. Brands
    Brand.objects.all().delete()
    brand_names = [f"Brand{idx}" for idx in range(1, 11)]  # Brand1..Brand10
    for name in brand_names:
        Brand.objects.create(name=name, description=f"Brand: {name}")
    print(f"   Đã seed {Brand.objects.count()} Brands.")

# --------------------------------------------
# 5. Seed Users
# --------------------------------------------
def seed_users():
    print("→ Bắt đầu seed Users …")
    User.objects.all().delete()

    first_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy",
                   "Kim", "Leo", "Mona", "Nina", "Oscar", "Peggy", "Quentin", "Rita", "Sam", "Trudy"]
    last_names = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Phan", "Vu", "Vo", "Do", "Duong"]

    created = []
    for i in range(20):  # tạo 20 user
        first = random.choice(first_names)
        last = random.choice(last_names)
        username = random_username(first, last)
        email = f"{username}@example.com"
        password = random_password()

        u = User.objects.create(
            first_name=first,
            last_name=last,
            username=username,
            email=email,
            password_hash=password,
            phone=f"0912{random.randint(100000,999999)}",
            gender=random.choice([0,1]),
            role="customer",
            status_enum=StatusEnum.ACTIVE.value
        )
        created.append(u)
    print(f"   Đã seed {len(created)} Users.")

# --------------------------------------------
# 6. Seed Products + SubProducts + ProductSubProduct
# --------------------------------------------

def seed_products_and_variants(products_csv_path, subproducts_csv_path):
    """
    Đọc dữ liệu từ 2 file CSV (products_csv_path, subproducts_csv_path),
    xóa sạch dữ liệu cũ, tạo lại Product và SubProduct, rồi liên kết qua ProductSubProduct.
    """

    # 1. Xóa sạch dữ liệu cũ
    ProductSubProduct.objects.all().delete()
    SubProduct.objects.all().delete()
    Product.objects.all().delete()

    # Dùng transaction để đảm bảo atomicity (nếu muốn)
    with transaction.atomic():
        # 2. Đọc file products.csv và tạo Product
        # Lưu tạm vào dict: key = product_id (string), value = instance Product
        products_map = {}

        with open(products_csv_path, mode='r', encoding='utf-8') as f_prod:
            reader = csv.DictReader(f_prod)
            for row in reader:
                # Lấy từng trường từ CSV
                prod_id = row.get('product_id')
                name = row.get('product_name')
                description = row.get('product_description') or ""
                image_url = row.get('product_image') or ""
                brand_id = row.get('product_brand_id')
                category_id = row.get('product_category_id')

                # Lấy Brand và Category từ database (nếu tồn tại)
                brand = None
                if brand_id:
                    try:
                        brand = Brand.objects.get(id=int(brand_id))
                    except Brand.DoesNotExist:
                        brand = None

                category = None
                if category_id:
                    try:
                        category = Category.objects.get(id=int(category_id))
                    except Category.DoesNotExist:
                        category = None

                # Tạo Product mới
                p = Product.objects.create(
                    name=name,
                    description=description,
                    image=image_url,
                    brand=brand,
                    category=category,
                    status_enum=StatusEnum.ACTIVE.value
                )
                # Lưu vào map để khi tạo subproduct dễ lookup
                products_map[str(prod_id)] = p

        # 3. Đọc file subproducts.csv và tạo SubProduct + ProductSubProduct
        count_sub = 0
        with open(subproducts_csv_path, mode='r', encoding='utf-8') as f_sub:
            reader = csv.DictReader(f_sub)
            for row in reader:
                prod_id = row.get('product_id')
                # Nếu không tìm thấy Product tương ứng, bỏ qua
                if prod_id not in products_map:
                    continue

                parent_product = products_map[prod_id]

                # Lấy các trường cho SubProduct
                # Chuyển sang đúng kiểu dữ liệu
                old_price_raw = row.get('subproduct_old_price') or "0"
                price_raw = row.get('product_price') or "0"
                discount_raw = row.get('subproduct_discount_percentage') or "0"
                saled_raw = row.get('product_saled_per_month') or "0"
                stock_raw = row.get('product_stock') or "0"

                try:
                    old_price = int(old_price_raw)
                except ValueError:
                    old_price = 0

                try:
                    price = int(price_raw)
                except ValueError:
                    price = 0

                try:
                    discount_pct = Decimal(discount_raw)
                except:
                    discount_pct = Decimal("0")

                try:
                    saled_per_month = int(saled_raw)
                except ValueError:
                    saled_per_month = 0

                try:
                    stock = int(stock_raw)
                except ValueError:
                    stock = 0

                color = row.get('color') or ""
                size = row.get('size') or ""
                sub_image = row.get('product_image') or ""
                specs = row.get('product_specs') or ""

                # Tạo SubProduct
                sp = SubProduct.objects.create(
                    old_price=old_price,
                    price=price,
                    discount_percentage=discount_pct,
                    saled_per_month=saled_per_month,
                    stock=stock,
                    color=color,
                    size=size,
                    image=sub_image,
                    specification=specs,
                    status_enum=StatusEnum.ACTIVE.value
                )

                # Tạo liên kết ProductSubProduct
                ProductSubProduct.objects.create(
                    product=parent_product,
                    sub_product=sp,
                    status_enum=StatusEnum.ACTIVE.value
                )
                count_sub += 1

    # In ra log kết quả
    total_prod = len(products_map)
    print(f"→ Đã seed xong {total_prod} Product và {count_sub} SubProduct + ProductSubProduct.")

# --------------------------------------------
# 7. Seed WishList và CartItem
# --------------------------------------------
def seed_wishlist_and_cart():
    print("→ Bắt đầu seed WishList và CartItem …")
    Wishlist.objects.all().delete()
    Cart.objects.all().delete()

    users = list(User.objects.all())
    # Lấy ngẫu nhiên tất cả SubProduct
    subs = list(SubProduct.objects.all())

    wl_count = 0
    ci_count = 0

    # Mỗi user thêm 2–5 wishlist
    for u in users:
        to_wishlist = random.sample(subs, k=min(len(subs), random.randint(4, 6)))
        for sp in to_wishlist:
            # unique_together: (user, sub_product)
            Wishlist.objects.get_or_create(
                user=u,
                sub_product=sp,
                defaults={"status_enum": StatusEnum.ACTIVE.value}
            )
            wl_count += 1

    # Mỗi user thêm 3–6 cart items (có thể lặp sub product)
    for u in users:
        to_cart = random.sample(subs, k=min(len(subs), random.randint(5, 8)))
        for sp in to_cart:
            quantity = random.randint(1, 3)
            Cart.objects.get_or_create(
                user=u,
                sub_product=sp,
                defaults={"quantity": quantity, "status_enum": StatusEnum.ACTIVE.value}
            )
            ci_count += 1

    print(f"   Đã seed {wl_count} WishList items và {ci_count} CartItem items.")


def seed_compare():
    print("→ Bắt đầu seed CompareProduct …")
    CompareProduct.objects.all().delete()

    users = list(User.objects.all())
    # Lấy ngẫu nhiên tất cả SubProduct
    subs = list(SubProduct.objects.all())

    wl_count = 0

    # Mỗi user thêm 2–5 CompareProduct
    for u in users:
        to_wishlist = random.sample(subs, k=min(len(subs), random.randint(2, 6)))
        for sp in to_wishlist:
            # unique_together: (user, sub_product)
            CompareProduct.objects.get_or_create(
                user=u,
                sub_product=sp,
                defaults={"status_enum": StatusEnum.ACTIVE.value}
            )
            wl_count += 1
            
    print(f"   Đã seed {wl_count} WishList items")
# --------------------------------------------
# 8. Seed Reviews
# --------------------------------------------
def seed_reviews():
    print("→ Bắt đầu seed Reviews …")
    Review.objects.all().delete()

    users = list(User.objects.all())
    subs = list(SubProduct.objects.all())

    rv_count = 0
    # Tạo 200 review ngẫu nhiên
    for i in range(200):
        u = random.choice(users)
        sp = random.choice(subs)
        rating = random.randint(1, 5)
        comment = f"Comment mẫu {i} cho {sp.color}-{sp.size}"
        Review.objects.create(
            user=u,
            sub_product=sp,
            rating=rating,
            comment=comment,
            status_enum=StatusEnum.ACTIVE.value
        )
        rv_count += 1

    print(f"   Đã seed {rv_count} Reviews.")

# --------------------------------------------
# 9. Seed Coupons
# --------------------------------------------
def seed_coupons():
    print("→ Bắt đầu seed Coupons …")
    Coupon.objects.all().delete()

    now = datetime.now()
    cp_count = 0
    for i in range(10):
        code = f"CODE{i}XYZ"
        discount_pct = round(random.uniform(5, 50), 2)
        quantity = random.randint(10, 100)
        valid_from = now - timedelta(days=random.randint(1, 10))
        valid_until = now + timedelta(days=random.randint(10, 30))
        Coupon.objects.create(
            code=code,
            discount_percentage=Decimal(discount_pct),
            quantity=quantity,
            valid_from=valid_from,
            valid_until=valid_until,
            status_enum=StatusEnum.ACTIVE.value
        )
        cp_count += 1

    print(f"   Đã seed {cp_count} Coupons.")

# --------------------------------------------
# 10. Seed PaymentMethod
# --------------------------------------------
def seed_payment_methods():
    print("→ Bắt đầu seed PaymentMethod …")
    PaymentMethod.objects.all().delete()

    methods = [
        ("Credit Card", "Thanh toán bằng thẻ tín dụng"),
        ("PayPal", "Thanh toán qua PayPal"),
        ("COD", "Thanh toán khi nhận hàng"),
        ("Bank Transfer", "Chuyển khoản ngân hàng"),
    ]
    pm_count = 0
    for name, desc in methods:
        PaymentMethod.objects.create(name=name, description=desc, status_enum=StatusEnum.ACTIVE.value)
        pm_count += 1

    print(f"   Đã seed {pm_count} PaymentMethod(s).")

# --------------------------------------------
# 11. Seed Orders, OrderItem, Payment, Shipping
# --------------------------------------------
def seed_orders_payments_shipping():
    print("→ Bắt đầu seed Orders, OrderItem, Payment, Shipping …")
    Order.objects.all().delete()
    OrderDetail.objects.all().delete()
    Payment.objects.all().delete()
    Shipping.objects.all().delete()

    users = list(User.objects.all())
    subs = list(SubProduct.objects.all())
    payment_methods = list(PaymentMethod.objects.all())

    order_count = 0
    oi_count = 0
    pay_count = 0
    ship_count = 0

    for i in range(50):
        u = random.choice(users)
        # Chọn 1–3 subproduct cho order
        chosen_subs = random.sample(subs, k=random.randint(1, 3))
        subtotal = 0
        order = Order.objects.create(
            user=u,
            subtotal=0,
            tax=0,
            discount=0,
            shipping_cost=0,
            total_price=0,
            status="pending",
            status_enum=StatusEnum.ACTIVE.value
        )
        order_count += 1

        # Tạo OrderItem
        for sp in chosen_subs:
            quantity = random.randint(1, 2)
            price = sp.price
            oi = OrderDetail.objects.create(
                order=order,
                sub_product=sp,
                quantity=quantity,
                price=price,
                status_enum=StatusEnum.ACTIVE.value
            )
            oi_count += 1
            subtotal += price * quantity

        # Cập nhật subtotal, tax (10%), shipping (20k), total
        tax = int(subtotal * 0.1)
        shipping_cost = 20000
        discount = random.choice([0, 10000, 20000])
        total_price = subtotal + tax + shipping_cost - discount

        order.subtotal = subtotal
        order.tax = tax
        order.discount = discount
        order.shipping_cost = shipping_cost
        order.total_price = total_price
        order.status = random.choice(["pending", "processing", "shipped", "completed"])
        order.save()

        # Tạo Payment (mỗi order 1 payment)
        pm = random.choice(payment_methods)
        payment = Payment.objects.create(
            order=order,
            payment_method=pm,
            status=random.choice(["paid", "failed", "pending"]),
            status_enum=StatusEnum.ACTIVE.value
        )
        pay_count += 1

        # Tạo Shipping (mỗi order 1 shipping)
        tracking_no = f"TRK{order.id}{random.randint(100000,999999)}"
        ship = Shipping.objects.create(
            order=order,
            tracking_number=tracking_no,
            estimate_delivery_date=datetime.now().date() + timedelta(days=random.randint(2,7)),
            status=random.choice(["pending", "shipped", "in_transit", "out_for_delivery", "delivered"]),
            status_enum=StatusEnum.ACTIVE.value
        )
        ship_count += 1

    print(f"   Đã seed {order_count} Orders, {oi_count} OrderItems, {pay_count} Payments, {ship_count} Shippings.")

# --------------------------------------------
# 12. Hàm chính: gọi lần lượt các seed
# --------------------------------------------
def run_all_seeds():
    # seed_categories_materials_brands()
    # seed_users()
    # seed_products_and_variants(r'D:\CapstoneProject\Codetest\unique_product_descriptions.csv',r'D:\CapstoneProject\Codetest\test.csv')
    # seed_wishlist_and_cart()
    # seed_compare()
    seed_reviews()
    # seed_coupons()
    # seed_payment_methods()
    # seed_orders_payments_shipping()
    print("\n🎉 Hoàn tất seed toàn bộ dữ liệu mẫu! 🎉")

if __name__ == "__main__":
    run_all_seeds()
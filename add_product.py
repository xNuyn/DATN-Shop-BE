import django
import os
import sys

# Thiết lập đường dẫn và môi trường Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")  # Cập nhật đường dẫn settings nếu khác
django.setup()

from products.models import Category, Brand, Product  # Cập nhật đúng đường dẫn model nếu app tên khác

# Lấy tất cả danh mục (categories) và thương hiệu (brands)
categories = Category.objects.all()
brands = Brand.objects.all()

# Dữ liệu sản phẩm
products_data = [
    {"name": "Samsung Galaxy S21", "description": "Điện thoại Samsung Galaxy S21", "category": "Điện thoại", "brand": "Samsung", "image": "image_s21.jpg"},
    {"name": "iPhone 13", "description": "Điện thoại iPhone 13", "category": "Điện thoại", "brand": "iPhone", "image": "image_iphone13.jpg"},
    {"name": "Xiaomi Mi 11", "description": "Điện thoại Xiaomi Mi 11", "category": "Điện thoại", "brand": "Xiaomi", "image": "image_mi11.jpg"},
    {"name": "Oppo F19", "description": "Điện thoại Oppo F19", "category": "Điện thoại", "brand": "Oppo", "image": "image_oppoF19.jpg"},
    {"name": "Dell XPS 13", "description": "Laptop Dell XPS 13", "category": "Laptop", "brand": "Dell", "image": "image_dellXPS13.jpg"},
    {"name": "Acer Aspire 5", "description": "Laptop Acer Aspire 5", "category": "Laptop", "brand": "Acer", "image": "image_acerAspire5.jpg"},
    {"name": "Asus ZenBook 14", "description": "Laptop Asus ZenBook 14", "category": "Laptop", "brand": "Asus", "image": "image_asusZenbook14.jpg"},
    {"name": "MacBook Air", "description": "Laptop MacBook Air", "category": "Laptop", "brand": "Mac", "image": "image_macbookAir.jpg"},
]

# Tạo sản phẩm cho từng dữ liệu
for product_data in products_data:
    # Lấy danh mục và thương hiệu tương ứng
    category = categories.filter(name=product_data["category"]).first()
    brand = brands.filter(name=product_data["brand"]).first()
    
    # Thêm sản phẩm vào cơ sở dữ liệu
    if category and brand:
        product, created = Product.objects.get_or_create(
            name=product_data["name"],
            description=product_data["description"],
            category=category,
            brand=brand,
            image=product_data["image"]
        )
        if created:
            print(f"Đã thêm sản phẩm: {product_data['name']}")
        else:
            print(f"Sản phẩm đã tồn tại: {product_data['name']}")
    else:
        print(f"Lỗi: Không tìm thấy danh mục hoặc thương hiệu cho sản phẩm {product_data['name']}")

print("✅ Hoàn thành thêm dữ liệu sản phẩm.")

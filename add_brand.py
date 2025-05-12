import django
import os
import sys

# Thiết lập đường dẫn và môi trường Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")  # Cập nhật đường dẫn settings nếu khác
django.setup()

from products.models import Brand  # Cập nhật đúng đường dẫn model nếu app tên khác

# Thêm dữ liệu vào bảng Brands
brands = {
    "Samsung": {"description": "Một trong những thương hiệu điện thoại hàng đầu thế giới."},
    "iPhone": {"description": "Apple, hãng điện thoại nổi tiếng của Mỹ."},
    "Xiaomi": {"description": "Thương hiệu điện thoại Trung Quốc nổi bật."},
    "Oppo": {"description": "Thương hiệu điện thoại từ Trung Quốc, được yêu thích ở nhiều quốc gia."},
    "Dell": {"description": "Một trong những thương hiệu laptop nổi tiếng toàn cầu."},
    "Acer": {"description": "Hãng sản xuất laptop và thiết bị điện tử đến từ Đài Loan."},
    "Asus": {"description": "Nổi tiếng với các dòng laptop gaming và linh kiện máy tính."},
    "Mac": {"description": "Apple, thương hiệu nổi bật trong dòng laptop cao cấp."},
}

for name, data in brands.items():
    brand, _ = Brand.objects.get_or_create(name=name, defaults={
        "description": data["description"]
    })
    print(f"Đã thêm hoặc tồn tại: {name}")

print("✅ Hoàn thành thêm dữ liệu thương hiệu.")

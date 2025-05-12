import django
import os
import sys

# Thiết lập đường dẫn và môi trường Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")  # Cập nhật đường dẫn settings nếu khác
django.setup()

from products.models import Category  # Cập nhật đúng đường dẫn model nếu app tên khác

# Thêm các danh mục cha
categories = {
    "Điện thoại": {"parent": None},
    "Laptop": {"parent": None},
}

category_objects = {}

for name, data in categories.items():
    category, _ = Category.objects.get_or_create(name=name, defaults={
        "parent": data["parent"]
    })
    category_objects[name] = category
    print(f"Đã thêm hoặc tồn tại: {name}")

# Thêm các danh mục con
subcategories = {
    "Samsung": {"parent": "Điện thoại"},
    "iPhone": {"parent": "Điện thoại"},
    "Xiaomi": {"parent": "Điện thoại"},
    "Oppo": {"parent": "Điện thoại"},
    "Dell": {"parent": "Laptop"},
    "Acer": {"parent": "Laptop"},
    "Asus": {"parent": "Laptop"},
    "Mac": {"parent": "Laptop"},
}

for name, data in subcategories.items():
    parent_category = category_objects.get(data["parent"])
    category, _ = Category.objects.get_or_create(name=name, defaults={
        "parent": parent_category
    })
    print(f"Đã thêm hoặc tồn tại: {name}")

print("✅ Hoàn thành thêm dữ liệu danh mục điện thoại & laptop.")

import django
import os
import sys


# Thiết lập đường dẫn và môi trường Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")  # Cập nhật đường dẫn settings nếu khác
django.setup()

import json
from products.models import Product, SubProduct, ProductSubProduct  # thay 'myapp' bằng tên app của bạn

# Dữ liệu sub_products (copy đoạn JSON đầy đủ ở trên vào biến này)
data = [
  {
    "product_name": "Samsung Galaxy S21",
    "sub_products": [
      {
        "old_price": 19829206,
        "price": 17421037,
        "color": "Trắng",
        "size": "128GB",
        "stock": 72,
        "image": "samsung_galaxy_s21_0.jpg",
        "specification": "Samsung Galaxy S21 - bản Trắng 128GB",
        "discount_percentage": 12.14
      },
      {
        "old_price": 18226925,
        "price": 13950160,
        "color": "Đỏ",
        "size": "512GB",
        "stock": 70,
        "image": "samsung_galaxy_s21_1.jpg",
        "specification": "Samsung Galaxy S21 - bản Đỏ 512GB",
        "discount_percentage": 23.46
      },
      {
        "old_price": 24862437,
        "price": 21560494,
        "color": "Trắng",
        "size": "128GB",
        "stock": 26,
        "image": "samsung_galaxy_s21_2.jpg",
        "specification": "Samsung Galaxy S21 - bản Trắng 128GB",
        "discount_percentage": 13.28
      }
    ]
  },
  {
    "product_name": "iPhone 13",
    "sub_products": [
      {
        "old_price": 26173097,
        "price": 21863877,
        "color": "Trắng",
        "size": "256GB",
        "stock": 75,
        "image": "iphone_13_0.jpg",
        "specification": "iPhone 13 - bản Trắng 256GB",
        "discount_percentage": 16.47
      },
      {
        "old_price": 27872029,
        "price": 25023602,
        "color": "Xanh",
        "size": "64GB",
        "stock": 57,
        "image": "iphone_13_1.jpg",
        "specification": "iPhone 13 - bản Xanh 64GB",
        "discount_percentage": 10.24
      },
      {
        "old_price": 22964685,
        "price": 20715629,
        "color": "Xanh",
        "size": "64GB",
        "stock": 58,
        "image": "iphone_13_2.jpg",
        "specification": "iPhone 13 - bản Xanh 64GB",
        "discount_percentage": 9.78
      }
    ]
  },
  {
    "product_name": "Xiaomi Mi 11",
    "sub_products": [
      {
        "old_price": 28903539,
        "price": 25696415,
        "color": "Đen",
        "size": "64GB",
        "stock": 39,
        "image": "xiaomi_mi_11_0.jpg",
        "specification": "Xiaomi Mi 11 - bản Đen 64GB",
        "discount_percentage": 11.1
      },
      {
        "old_price": 25471165,
        "price": 21234678,
        "color": "Trắng",
        "size": "64GB",
        "stock": 60,
        "image": "xiaomi_mi_11_1.jpg",
        "specification": "Xiaomi Mi 11 - bản Trắng 64GB",
        "discount_percentage": 16.65
      },
      {
        "old_price": 18907785,
        "price": 16232411,
        "color": "Trắng",
        "size": "256GB",
        "stock": 85,
        "image": "xiaomi_mi_11_2.jpg",
        "specification": "Xiaomi Mi 11 - bản Trắng 256GB",
        "discount_percentage": 14.13
      }
    ]
  },
  {
    "product_name": "Oppo F19",
    "sub_products": [
      {
        "old_price": 23922419,
        "price": 19298355,
        "color": "Trắng",
        "size": "64GB",
        "stock": 42,
        "image": "oppo_f19_0.jpg",
        "specification": "Oppo F19 - bản Trắng 64GB",
        "discount_percentage": 19.31
      },
      {
        "old_price": 27098793,
        "price": 23766799,
        "color": "Đen",
        "size": "256GB",
        "stock": 60,
        "image": "oppo_f19_1.jpg",
        "specification": "Oppo F19 - bản Đen 256GB",
        "discount_percentage": 12.3
      },
      {
        "old_price": 22623131,
        "price": 20286500,
        "color": "Trắng",
        "size": "256GB",
        "stock": 29,
        "image": "oppo_f19_2.jpg",
        "specification": "Oppo F19 - bản Trắng 256GB",
        "discount_percentage": 10.33
      }
    ]
  },
  {
    "product_name": "Dell XPS 13",
    "sub_products": [
      {
        "old_price": 21140453,
        "price": 17966284,
        "color": "Đỏ",
        "size": "64GB",
        "stock": 63,
        "image": "dell_xps_13_0.jpg",
        "specification": "Dell XPS 13 - bản Đỏ 64GB",
        "discount_percentage": 15.01
      },
      {
        "old_price": 23830279,
        "price": 19269607,
        "color": "Đỏ",
        "size": "64GB",
        "stock": 40,
        "image": "dell_xps_13_1.jpg",
        "specification": "Dell XPS 13 - bản Đỏ 64GB",
        "discount_percentage": 19.1
      },
      {
        "old_price": 27450696,
        "price": 24024033,
        "color": "Trắng",
        "size": "64GB",
        "stock": 49,
        "image": "dell_xps_13_2.jpg",
        "specification": "Dell XPS 13 - bản Trắng 64GB",
        "discount_percentage": 12.47
      }
    ]
  },
  {
    "product_name": "Acer Aspire 5",
    "sub_products": [
      {
        "old_price": 20249872,
        "price": 17598349,
        "color": "Xanh",
        "size": "64GB",
        "stock": 40,
        "image": "acer_aspire_5_0.jpg",
        "specification": "Acer Aspire 5 - bản Xanh 64GB",
        "discount_percentage": 13.09
      },
      {
        "old_price": 19499128,
        "price": 17501702,
        "color": "Xanh",
        "size": "128GB",
        "stock": 72,
        "image": "acer_aspire_5_1.jpg",
        "specification": "Acer Aspire 5 - bản Xanh 128GB",
        "discount_percentage": 10.23
      },
      {
        "old_price": 28601911,
        "price": 23805386,
        "color": "Trắng",
        "size": "512GB",
        "stock": 69,
        "image": "acer_aspire_5_2.jpg",
        "specification": "Acer Aspire 5 - bản Trắng 512GB",
        "discount_percentage": 16.78
      }
    ]
  },
  {
    "product_name": "Asus ZenBook 14",
    "sub_products": [
      {
        "old_price": 18955723,
        "price": 17039995,
        "color": "Đen",
        "size": "256GB",
        "stock": 60,
        "image": "asus_zenbook_14_0.jpg",
        "specification": "Asus ZenBook 14 - bản Đen 256GB",
        "discount_percentage": 10.1
      },
      {
        "old_price": 25772323,
        "price": 21001367,
        "color": "Trắng",
        "size": "512GB",
        "stock": 45,
        "image": "asus_zenbook_14_1.jpg",
        "specification": "Asus ZenBook 14 - bản Trắng 512GB",
        "discount_percentage": 18.53
      },
      {
        "old_price": 27875050,
        "price": 24310376,
        "color": "Đen",
        "size": "128GB",
        "stock": 94,
        "image": "asus_zenbook_14_2.jpg",
        "specification": "Asus ZenBook 14 - bản Đen 128GB",
        "discount_percentage": 12.79
      }
    ]
  },
  {
    "product_name": "MacBook Air",
    "sub_products": [
      {
        "old_price": 28423241,
        "price": 25317435,
        "color": "Trắng",
        "size": "128GB",
        "stock": 64,
        "image": "macbook_air_0.jpg",
        "specification": "MacBook Air - bản Trắng 128GB",
        "discount_percentage": 10.93
      },
      {
        "old_price": 21517756,
        "price": 17971955,
        "color": "Trắng",
        "size": "128GB",
        "stock": 86,
        "image": "macbook_air_1.jpg",
        "specification": "MacBook Air - bản Trắng 128GB",
        "discount_percentage": 16.45
      },
      {
        "old_price": 27336829,
        "price": 24731469,
        "color": "Đen",
        "size": "256GB",
        "stock": 20,
        "image": "macbook_air_2.jpg",
        "specification": "MacBook Air - bản Đen 256GB",
        "discount_percentage": 9.52
      }
    ]
  }
]

# Tạo SubProduct và bản ghi liên kết
for entry in data:
    try:
        product = Product.objects.get(name=entry["product_name"])
    except Product.DoesNotExist:
        print(f"❌ Không tìm thấy sản phẩm: {entry['product_name']}")
        continue

    for sp in entry["sub_products"]:
        sub_product = SubProduct.objects.create(
            old_price=sp["old_price"],
            price=sp["price"],
            color=sp["color"],
            size=sp["size"],
            stock=sp["stock"],
            image=sp["image"],
            specification=sp["specification"],
            discount_percentage=sp["discount_percentage"]
        )

        # Tạo bản ghi trong bảng liên kết
        ProductSubProduct.objects.create(
            product=product,
            sub_product=sub_product
        )

        print(f"✅ Đã thêm SubProduct và liên kết cho: {sp['specification']}")

print("🎉 Hoàn tất thêm SubProducts và bảng liên kết.")

import os
import sys
import json
import django

# Thiết lập môi trường Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from products.models import SubProduct, ProductSubProduct

def get_structured_data():
    result = []

    sub_products = SubProduct.objects.all().select_related()

    for sub in sub_products:
        # Get linked Product via intermediate table
        try:
            prod_sub = ProductSubProduct.objects.get(sub_product=sub)
            product = prod_sub.product
        except ProductSubProduct.DoesNotExist:
            continue

        # Build metadata
        metadata = {
            "id_sub_product": sub.id,
            "name_product": product.name,
            "category": product.category.name,
            "brand": product.brand.name,
            "image_url": product.image,
            "color": sub.color,
            "size": sub.size,
            "price": sub.price,
            "stock": sub.stock,
            "sold_per_month": sub.saled_per_month,
            "sub_image_url": sub.image
        }

        # Content từ mô tả
        content = f"{product.name} - {product.brand} ({sub.color}, {sub.size})\n" \
                  f"{product.description}\n{sub.specification}"

        result.append({
            "metadata": metadata,
            "content": content
        })

    return result

# Export to JSON file
output_file = "retrieval_data.json"
data = get_structured_data()
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
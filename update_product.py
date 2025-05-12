import django
import os
import sys


# Thiết lập đường dẫn và môi trường Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from products.models import Product

updated_descriptions = {
    "Samsung Galaxy S21": "Samsung Galaxy S21 là dòng điện thoại cao cấp với thiết kế hiện đại, sở hữu màn hình Dynamic AMOLED 2X 6.2 inch sắc nét, hiệu năng mạnh mẽ với chip Exynos 2100 và hệ thống 3 camera linh hoạt, phù hợp cho cả công việc và giải trí.",
    "iPhone 13": "iPhone 13 đến từ Apple sở hữu thiết kế tinh tế với khung viền phẳng hiện đại, sử dụng chip A15 Bionic mạnh mẽ, thời lượng pin cải thiện đáng kể và camera kép 12MP hỗ trợ chế độ chụp ảnh ban đêm sắc nét, mang lại trải nghiệm mượt mà cho người dùng.",
    "Xiaomi Mi 11": "Xiaomi Mi 11 là smartphone cao cấp với màn hình AMOLED 2K+ hỗ trợ 120Hz, chip Snapdragon 888 mạnh mẽ, camera 108MP chụp ảnh sắc nét cùng thiết kế mỏng nhẹ tinh tế, mang lại hiệu năng vượt trội trong phân khúc giá.",
    "Oppo F19": "Oppo F19 nổi bật với thiết kế mỏng nhẹ, màn hình AMOLED 6.43 inch sắc nét, pin dung lượng 5000mAh đi kèm sạc nhanh 33W, và cụm camera AI giúp người dùng chụp ảnh chất lượng trong nhiều điều kiện ánh sáng khác nhau.",
    "Dell XPS 13": "Dell XPS 13 là dòng laptop cao cấp nổi bật với thiết kế kim loại nguyên khối, màn hình InfinityEdge 13.4 inch viền mỏng, độ phân giải cao, hiệu năng mạnh mẽ với chip Intel thế hệ 11 và thời lượng pin ấn tượng, phù hợp cho người dùng doanh nhân và sáng tạo nội dung.",
    "Acer Aspire 5": "Acer Aspire 5 là laptop tầm trung sở hữu hiệu năng ổn định với bộ vi xử lý AMD Ryzen hoặc Intel Core, màn hình 15.6 inch Full HD, thiết kế đơn giản, chắc chắn, phù hợp cho học sinh, sinh viên hoặc người dùng văn phòng.",
    "Asus ZenBook 14": "Asus ZenBook 14 là mẫu ultrabook siêu mỏng nhẹ với vỏ kim loại sang trọng, chip Intel thế hệ mới, màn hình 14 inch viền mỏng NanoEdge sắc nét và bàn di chuột tích hợp NumberPad thông minh, là sự lựa chọn lý tưởng cho người dùng di chuyển nhiều.",
    "MacBook Air": "MacBook Air phiên bản dùng chip Apple M1 mang lại hiệu năng vượt trội, thời lượng pin lên tới 18 giờ, thiết kế mỏng nhẹ đặc trưng và hệ điều hành macOS mượt mà, là lựa chọn hoàn hảo cho người dùng yêu thích sự ổn định và tối ưu hóa phần cứng.",
}

for name, desc in updated_descriptions.items():
    try:
        product = Product.objects.get(name=name)
        product.description = desc
        product.save()
        print(f"✅ Đã cập nhật: {name}")
    except Product.DoesNotExist:
        print(f"❌ Không tìm thấy sản phẩm: {name}")

# views.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncYear, TruncMonth, TruncWeek, TruncDay
from rest_framework.response import Response
from rest_framework import status

from orders.models import Order, OrderDetail
from products.models import SubProduct
from .serializers import DashboardSerializer
from rest_framework.views import APIView
from authentication.permissions import IsAdminPermission


class DashboardView(APIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        time = request.query_params.get("time", "all")  # all | year | month | week

        # Lọc đơn hàng hợp lệ (đã được giao hàng)
        valid_orders = Order.objects.filter(status=Order.OrderStatus.COMPLETED)

        # Thống kê tổng
        total_revenue = valid_orders.aggregate(total=Sum('total_price'))['total'] or 0
        total_users = valid_orders.values('user').distinct().count()
        total_orders = valid_orders.count()
        total_products = OrderDetail.objects.filter(order__in=valid_orders).values('sub_product').distinct().count()

        # Chart group theo từng mức thời gian
        if time == "all":
            group_by = TruncYear('created_at')
            label_format = "%Y"
        elif time == "year":
            group_by = TruncMonth('created_at')
            label_format = "%Y-%m"
        elif time == "month":
            group_by = TruncWeek('created_at')
            label_format = "Week %W"
        elif time == "week":
            group_by = TruncDay('created_at')
            label_format = "%Y-%m-%d"
        else:
            return Response({"detail": "Invalid time parameter"}, status=status.HTTP_400_BAD_REQUEST)

        chart_queryset = (
            valid_orders
            .annotate(period=group_by)
            .values('period')
            .annotate(
                revenue=Sum('total_price'),
                buyer_count=Count('user', distinct=True)
            )
            .order_by('period')
        )

        chart_data = [
            {
                "label": data["period"].strftime(label_format),
                "revenue": data["revenue"] or 0,
                "buyer_count": data["buyer_count"]
            }
            for data in chart_queryset
        ]

        serializer = DashboardSerializer({
            "total_revenue": total_revenue,
            "total_users": total_users,
            "total_orders": total_orders,
            "total_products": total_products,
            "chart_data": chart_data
        })

        return Response(serializer.data)
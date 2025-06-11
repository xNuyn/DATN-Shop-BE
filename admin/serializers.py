# serializers.py
from rest_framework import serializers

class DashboardChartSerializer(serializers.Serializer):
    label = serializers.CharField()
    revenue = serializers.IntegerField()
    buyer_count = serializers.IntegerField()

class DashboardSerializer(serializers.Serializer):
    total_revenue = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_products = serializers.IntegerField()
    chart_data = DashboardChartSerializer(many=True)
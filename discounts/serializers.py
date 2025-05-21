from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class CouponSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('id', 'code', 'discount_percentage', 'quantity', 'valid_from', 'valid_until', 'is_active', 'status_enum')
        read_only_fields = ('id', 'created_at')

class CouponUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ('created_at')
        
class CouponUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('code', 'discount_percentage', 'quantity', 'valid_from', 'valid_until', 'is_active', 'status_enum')
        read_only_fields = ('id', 'created_at')
    
class IdsCouponSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
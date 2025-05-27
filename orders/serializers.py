from rest_framework import serializers
from .models import Order, OrderDetail
from products.serializers import SubProductSerializerOutput

##-------------Order----------------##
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class OrderSerializerOutput(serializers.ModelSerializer):
    order_details = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ('id', 'user', 'subtotal', 'tax', 'discount', 'shipping_cost', 'total_price', 'status', 'created_at', 'status_enum', 'order_details')
        read_only_fields = ('id', 'created_at')

    def get_order_details(self, obj):
        order_details = obj.order_details.all()
        return OrderDetailSerializerOutput(order_details, many=True).data

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('subtotal', 'tax', 'discount', 'shipping_cost', 'total_price', 'status')
        read_only_fields = ('id', 'created_at')
    
class IdsOrderSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

##--------------Order Detail-------------##
class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = '__all__'

class OrderDetailSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerOutput()
    class Meta:
        model = OrderDetail
        fields = ('id', 'order', 'sub_product', 'quantity', 'price', 'status_enum')

class OrderDetailUpdateSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(required=True)
    sub_product_id = serializers.IntegerField(required=True)
    class Meta:
        model = OrderDetail
        fields = ('order_id', 'sub_product_id', 'quantity', 'price')
    
class IdsOrderDetailSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

from rest_framework import serializers
from .models import Cart, Wishlist
from products.serializers import *

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class CartSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerOutput()
    class Meta:
        model = Cart
        fields = ('id', 'user', 'sub_product', 'quantity')
        
class CartUpdateSerializer(serializers.ModelSerializer):
    sub_product_id = serializers.IntegerField(required=False)
    class Meta:
        model = Cart
        fields = ('sub_product_id', 'quantity')
    
class IdsCartSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class WishlistSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerOutput()
    class Meta:
        model = Wishlist
        fields = ('id', 'user', 'sub_product')
        
class WishlistUpdateSerializer(serializers.ModelSerializer):
    sub_product_id = serializers.IntegerField(required=False)
    class Meta:
        model = Wishlist
        fields = ('sub_product_id',)
    
class IdsWishlistSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
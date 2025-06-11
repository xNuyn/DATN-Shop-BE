from rest_framework import serializers
from .models import CompareProduct
from products.serializers import *

class CompareProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompareProduct
        fields = '__all__'

class CompareProductSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerForOrder()
    class Meta:
        model = CompareProduct
        fields = ('id', 'user', 'sub_product')
        
class CompareProductUpdateSerializer(serializers.ModelSerializer):
    sub_product_id = serializers.IntegerField(required=False)
    class Meta:
        model = CompareProduct
        fields = ('sub_product_id',)
    
class IdsCompareProductSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
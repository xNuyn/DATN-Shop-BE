from rest_framework import serializers
from .models import Product, Category, Brand, SubProduct, ProductSubProduct

##-------------Product------------##
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class ProductSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'category', 'brand', 'image')
        read_only_fields = ('id', 'created_at')
        
class ProductUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = Product
        fields = ('name', 'description', 'category', 'brand', 'image')
        read_only_fields = ('id', 'created_at')
    
class IdsProductSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

##--------------Catogery--------------##
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategorySerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')
        
class CategoryUpdateSerializer(serializers.ModelSerializer):
    parent_id= serializers.IntegerField(required=False)
    class Meta:
        model = Category
        fields = ('name', 'parent_id')
    
class IdsCategorySerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
##-------------Brand----------------##
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class BrandSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'description')
        
class BrandUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('name', 'description')
    
class IdsBrandSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
##---------------SubProduct---------------##
class SubProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubProduct
        fields = '__all__'

class SubProductSerializerOutput(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    class Meta:
        model = SubProduct
        fields = ('id', 'product', 'old_price', 'price', 'color', 'size', 'stock', 'image', 'specification', 'discount_percentage', 'saled_per_month')
        
    def get_product(self, obj):
        try:
            product_subproduct = obj.product.select_related('product').first()
            if product_subproduct:
                return ProductSerializerOutput(product_subproduct.product).data
            return None
        except ProductSubProduct.DoesNotExist:
            return None
        
class SubProductUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    product_id= serializers.ImageField(required=False)
    class Meta:
        model = SubProduct
        fields = ('old_price', 'price', 'color', 'size', 'stock', 'image', 'specification', 'discount_percentage', 'saled_per_month', 'product_id')
    
class IdsSubProductSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
##---------------ProductSubProduct---------------##
class ProductSubProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubProduct
        fields = '__all__'
        read_only_fields = ('id',)

class ProductSubProductSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = ProductSubProduct
        fields = ('id', 'product', 'sub_product')
        read_only_fields = ('id',)
        
class ProductSubProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubProduct
        fields = ('product', 'sub_product')
        read_only_fields = ('id',)
    
class IdsProductSubProductSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
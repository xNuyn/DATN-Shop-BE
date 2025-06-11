from rest_framework import serializers
from .models import Product, Category, Brand, SubProduct, ProductSubProduct
from app.models import StatusEnum
from django.db.models import Min, Max, Sum
from reviews.serializers import ReviewSerializerForSubP

##-------------Product------------##
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class ProductSerializerOutput(serializers.ModelSerializer):
    price_min = serializers.SerializerMethodField()
    price_max = serializers.SerializerMethodField()
    sold_per_month = serializers.SerializerMethodField()
    discount_percentage_max = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'category', 'brand', 'image','created_at', 'price_min', 'price_max', 'sold_per_month', 'discount_percentage_max')
        read_only_fields = ('id',)
        
    def get_price_min(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(min_price=Min('sub_product__price'))['min_price']

    def get_price_max(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(max_price=Max('sub_product__price'))['max_price']
        
    def get_sold_per_month(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(sold_per_month=Sum('sub_product__saled_per_month'))['sold_per_month']
        
    def get_discount_percentage_max(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE,
            sub_product__discount_percentage__isnull=False
        ).aggregate(max_discount=Max('sub_product__discount_percentage'))['max_discount']

class ProductSerializerDetail(serializers.ModelSerializer):
    price_min = serializers.SerializerMethodField()
    price_max = serializers.SerializerMethodField()
    sold_per_month = serializers.SerializerMethodField()
    sub_products = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", 'name', 'description', 'category', 'brand', 'image', 'price_min', 'price_max', 'sold_per_month', "sub_products"
        ]
        
    def get_category(self, obj):
        category = obj.category
        while category and category.parent is not None:
            category = category.parent
        return category.name if category else None
    
    def get_brand(self, obj):
        return obj.category.name if obj.category else None

    def get_price_min(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(min_price=Min('sub_product__price'))['min_price']

    def get_price_max(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(max_price=Max('sub_product__price'))['max_price']
        
    def get_sold_per_month(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(sold_per_month=Sum('sub_product__saled_per_month'))['sold_per_month']
    
    def get_sub_products(self, obj):
        sub_products = SubProduct.objects.filter(
            product__product=obj,
            product__status_enum=StatusEnum.ACTIVE,
            status_enum=StatusEnum.ACTIVE
        )
        return SubProductSerializer(sub_products, many=True).data
    
class ProductSerializerSerializerForOrder(serializers.ModelSerializer):
    price_min = serializers.SerializerMethodField()
    price_max = serializers.SerializerMethodField()
    sold_per_month = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", 'name', 'description', 'category', 'brand', 'image', 'price_min', 'price_max', 'sold_per_month'
        ]
        
    def get_category(self, obj):
        category = obj.category
        while category and category.parent is not None:
            category = category.parent
        return category.name if category else None
    
    def get_brand(self, obj):
        return obj.category.name if obj.category else None

    def get_price_min(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(min_price=Min('sub_product__price'))['min_price']

    def get_price_max(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(max_price=Max('sub_product__price'))['max_price']
        
    def get_sold_per_month(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(sold_per_month=Sum('sub_product__saled_per_month'))['sold_per_month']
        
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
    reviews = ReviewSerializerForSubP(many=True, read_only=True)
    class Meta:
        model = SubProduct
        fields = [
            'id',
            'old_price',
            'price',
            'color',
            'size',
            'stock',
            'image',
            'specification',
            'discount_percentage',
            'saled_per_month',
            'status_enum',
            'reviews',
        ]
        read_only_fields = ['reviews']

class SubProductSerializerOutput(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    reviews = ReviewSerializerForSubP(many=True, read_only=True)
    class Meta:
        model = SubProduct
        fields = ('id', 'product', 'old_price', 'price', 'color', 'size', 'stock', 'image', 'specification', 'discount_percentage', 'saled_per_month', 'reviews')
        read_only_fields = ['reviews']
        
    def get_product(self, obj):
        try:
            product_subproduct = obj.product.select_related('product').first()
            if product_subproduct:
                return ProductSerializerOutput(product_subproduct.product).data
            return None
        except ProductSubProduct.DoesNotExist:
            return None
        
class SubProductSerializerForOrder(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    class Meta:
        model = SubProduct
        fields = ('id', 'product', 'old_price', 'price', 'color', 'size', 'stock', 'image', 'specification', 'discount_percentage', 'saled_per_month')
        
    def get_product(self, obj):
        try:
            product_subproduct = obj.product.select_related('product').first()
            if product_subproduct:
                return ProductSerializerSerializerForOrder(product_subproduct.product).data
            return None
        except ProductSubProduct.DoesNotExist:
            return None
        
class SubProductSerializerForAdmin(serializers.ModelSerializer):
    reviews = ReviewSerializerForSubP(many=True, read_only=True)
    product = serializers.SerializerMethodField()
    class Meta:
        model = SubProduct
        fields = [
            'id',
            'old_price',
            'price',
            'color',
            'size',
            'stock',
            'image',
            'specification',
            'discount_percentage',
            'saled_per_month',
            'status_enum',
            'product',
            'reviews',
        ]
        read_only_fields = ['reviews']
        
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
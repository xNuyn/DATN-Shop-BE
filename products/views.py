import requests
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from products.models import Product, Category, Brand, SubProduct, ProductSubProduct
from products.serializers import (
    ProductSerializer, ProductSerializerOutput, ProductUpdateSerializer, IdsProductSerializer, ProductSerializerDetail,
    CategorySerializer, CategorySerializerOutput, CategoryUpdateSerializer, IdsCategorySerializer,
    BrandSerializer, BrandSerializerOutput, BrandUpdateSerializer, IdsBrandSerializer,
    SubProductSerializer, SubProductSerializerOutput, SubProductUpdateSerializer, IdsSubProductSerializer, SubProductSerializerForAdmin,
    ProductSubProductSerializer, ProductSubProductSerializerOutput, ProductSubProductUpdateSerializer, IdsProductSubProductSerializer
)
from app.serializers import ResponseSerializer
from app.models import StatusEnum
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from django.db.models import Sum, Min, Max, CharField, Value
from django.db.models import FilteredRelation
from django.db.models.functions import Concat


def soft_delete_subproduct(sub_product):
    if sub_product.status_enum != StatusEnum.DELETED.value:
        sub_product.status_enum = StatusEnum.DELETED.value
        sub_product.save()
        print(f"Soft deleted SubProduct: {sub_product}")

def soft_delete_product(product):
    if product.status_enum != StatusEnum.DELETED.value:
        product.status_enum = StatusEnum.DELETED.value
        product.save()
        print(f"Soft deleted Product: {product.name}")

    product_subproducts = product.sub_product.select_related('sub_product')
    for link in product_subproducts:
        soft_delete_subproduct(link.sub_product)

    for link in product_subproducts:
        if link.status_enum != StatusEnum.DELETED.value:
            link.status_enum = StatusEnum.DELETED.value
            link.save()

def recursive_soft_delete(category):
    if category.status_enum != StatusEnum.DELETED.value:
        category.status_enum = StatusEnum.DELETED.value
        category.save()
        print(f"Soft deleted Category: {category.name}")

    for product in category.products.all():
        soft_delete_product(product)

    for subcategory in category.subcategories.all():
        recursive_soft_delete(subcategory)
        
def soft_delete_brand(brand):
    if brand.status_enum != StatusEnum.DELETED.value:
        brand.status_enum = StatusEnum.DELETED.value
        brand.save()
        print(f"Soft deleted Brand: {brand.name}")
        
    for product in brand.products.all():
        soft_delete_product(product)

##-------------Product------------##
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action in ['list']:
            return ProductSerializerOutput
        elif self.action in ['retrieve']:
            return ProductSerializerDetail
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsProductSerializer
        return ProductSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Product._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("product list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("product retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=ProductUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("product create")
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        product = ProductSerializer(data=data)
        if product.is_valid():
            product.save()
        else:
            return Response(
                {"detail": "Product is invalid",  "errors": product.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"product": product.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        product = ProductSerializer(instance, data=data, partial=partial)
        product.is_valid(raise_exception=True)
        product.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("product partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        product = ProductSerializer(instance, data=data, partial=partial)
        product.is_valid(raise_exception=True)
        product.save()

        return Response(product.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("product destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'Product deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("product soft_delete")
        product = self.get_object()

        deleted = soft_delete_product(product)
        if not deleted:
            return Response({'detail': 'Product already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Product soft deleted successfully'}, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=False, methods=['post'], url_path='multiple-delete')
    def multiple_delete(self, request):
        print("product multiple_delete")
        ids = request.data.get('ids', [])

        if not ids or not isinstance(ids, list):
            return Response({'message': 'No valid product IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(id__in=ids)
        if not products.exists():
            return Response({'message': 'No products found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        deleted_count = 0
        for product in products:
            if soft_delete_product(product):
                deleted_count += 1

        if deleted_count == 0:
            return Response({'message': 'All products were already soft deleted.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': f'Soft deleted {deleted_count} product(s) successfully.'
        }, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('product multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No product IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        products = Product.objects.filter(id__in=ids) 
        if not products.exists():
            return Response({'message': 'No products found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for product in products:
            product.delete()
        return Response({'message': 'Products destroy successfully'}, status=status.HTTP_200_OK)
   
   
    
# class ProductSearchView(generics.ListAPIView):
#     serializer_class = ProductSerializer
#     permission_classes = []
    
#     def get_all_subcategories(self, parent_category):
#         subcategories = Category.objects.filter(parent=parent_category)
#         print("subcategories", subcategories)
#         all_subcategories = list(subcategories)
#         print("loi 1")
#         for subcategory in subcategories:
#             all_subcategories.extend(self.get_all_subcategories(subcategory))
#         return all_subcategories
    
#     def get_queryset(self):
#         name = self.request.query_params.get('name', None)
#         description = self.request.query_params.get('description', None)
#         category = self.request.query_params.get('category', None)
#         brand = self.request.query_params.get('brand', None)
#         sort_by = self.request.query_params.get('sort_by', None)
        
        
#         type_search_name = self.request.query_params.get('type_search_name', None)
#         type_search_description = self.request.query_params.get('type_search_description', None)
#         type_search_category = self.request.query_params.get('type_search_category', None)
#         type_search_brand = self.request.query_params.get('type_search_brand', None)
                
#         queryset = Product.objects.all()
#         queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value)
#         queryset = queryset.annotate(
#             active_sub_products=FilteredRelation(
#                 'sub_product__sub_product',
#                 condition=Q(sub_product__sub_product__status_enum=StatusEnum.ACTIVE.value)
#             ),
#             sold_per_month=Sum('active_sub_products__saled_per_month'),
#             min_price=Min('active_sub_products__price'),
#             max_price=Max('active_sub_products__price')
#         )
        
        
#         if name:
#             if type_search_name == 'exact':
#                 queryset = queryset.filter(name=name)
#             elif type_search_name == 'contains':
#                 queryset = queryset.filter(name__icontains=name)
#             elif type_search_name == 'startswith':
#                 queryset = queryset.filter(name__istartswith=name)
#             elif type_search_name == 'endswith':
#                 queryset = queryset.filter(name__iendswith=name)
#             else:
#                 raise ValidationError("Require name type search in ['exact', 'contains', 'startswith', 'endswith']")
#         if description:
#             if type_search_description == 'exact':
#                 queryset = queryset.filter(description=description)
#             elif type_search_description == 'contains':
#                 queryset = queryset.filter(description__icontains=description)
#             elif type_search_description == 'startswith':
#                 queryset = queryset.filter(description__istartswith=description)
#             elif type_search_description == 'endswith':
#                 queryset = queryset.filter(description__iendswith=description)
#             else:
#                 raise ValidationError("Require description type search in ['exact', 'contains', 'startswith', 'endswith']")

#         if category and type_search_category:
#             if type_search_category == 'exact':
#                 queryset = queryset.filter(category=category)
#             elif type_search_category == 'contains':
#                 queryset = queryset.filter(category__icontains=category)
#             elif type_search_category == 'startswith':
#                 queryset = queryset.filter(category__istartswith=category)
#             elif type_search_category == 'endswith':
#                 queryset = queryset.filter(category__iendswith=category)
#             elif type_search_category == 'parent':
#                 all_subcategories = self.get_all_subcategories(category)
#                 all_subcategories.append(category)
#                 queryset = queryset.filter(category__in=all_subcategories)
#             else:
#                 raise ValidationError("Require category type search in ['exact', 'contains', 'startswith', 'endswith', 'parent']")
            
#         if brand:
#             if type_search_brand == 'exact':
#                 queryset = queryset.filter(brand=brand)
#             elif type_search_brand == 'contains':
#                 queryset = queryset.filter(brand__icontains=brand)
#             elif type_search_brand == 'startswith':
#                 queryset = queryset.filter(brand__istartswith=brand)
#             elif type_search_brand == 'endswith':
#                 queryset = queryset.filter(brand__iendswith=brand)
#             else:
#                 raise ValidationError("Require brand type search in ['exact', 'contains', 'startswith', 'endswith']")
            
#         if sort_by:
#             if sort_by == 'bestseller': 
#                 queryset = queryset.order_by('-sold_per_month')
#             elif sort_by == 'lowtohigh':
#                 queryset = queryset.order_by('min_price')
#             elif sort_by == 'hightolow':
#                 queryset = queryset.order_by('-max_price')
#             else: 
#                 raise ValidationError("Require sort_by in ['bestseller', 'lowtohigh', 'hightolow']")
        
#         return queryset
    
    
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()        
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = ProductSerializerOutput(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        description = self.request.query_params.get('description', None)
        categories = self.request.query_params.get('categories', None)
        brands = self.request.query_params.get('brands', None)
        sort_by = self.request.query_params.get('sort_by', None)
        keyword = self.request.query_params.get('keyword', None)
        category_name = self.request.query_params.get('category_name', None)
        brand_name = self.request.query_params.get('brand_name', None)
        price = self.request.query_params.get('price', None)

        type_search_name = self.request.query_params.get('type_search_name', None)
        type_search_description = self.request.query_params.get('type_search_description', None)
        type_search_keyword = self.request.query_params.get('type_search_keyword', None)

        queryset = Product.objects.filter(status_enum=StatusEnum.ACTIVE.value)

        queryset = queryset.annotate(
            active_sub_products=FilteredRelation(
                'sub_product__sub_product',
                condition=Q(sub_product__sub_product__status_enum=StatusEnum.ACTIVE.value)
            ),
            sold_per_month=Sum('active_sub_products__saled_per_month'),
            min_price=Min('active_sub_products__price'),
            max_price=Max('active_sub_products__price'),
            text_search=Concat(
                'name', Value(' '), 
                'description', Value(' '),
                'category__parent__name', Value(' '), 
                'category__name', Value(' '),
                output_field=CharField()
            )
        )

        if name:
            if type_search_name == 'exact':
                queryset = queryset.filter(name=name)
            elif type_search_name == 'contains':
                queryset = queryset.filter(name__icontains=name)
            elif type_search_name == 'startswith':
                queryset = queryset.filter(name__istartswith=name)
            elif type_search_name == 'endswith':
                queryset = queryset.filter(name__iendswith=name)
            else:
                raise ValidationError("Require name type search in ['exact', 'contains', 'startswith', 'endswith']")

        if description:
            if type_search_description == 'exact':
                queryset = queryset.filter(description=description)
            elif type_search_description == 'contains':
                queryset = queryset.filter(description__icontains=description)
            elif type_search_description == 'startswith':
                queryset = queryset.filter(description__istartswith=description)
            elif type_search_description == 'endswith':
                queryset = queryset.filter(description__iendswith=description)
            else:
                raise ValidationError("Require description type search in ['exact', 'contains', 'startswith', 'endswith']")

        if categories:
            category_ids = [int(c.strip()) for c in categories.split(',') if c.strip().isdigit()]
            all_ids = set(category_ids)
            for cid in category_ids:
                subcats = self.get_all_subcategories(cid)
                all_ids.update([c.id for c in subcats])
            queryset = queryset.filter(category__in=all_ids)

        if brands:
            subcategory_ids = [int(b.strip()) for b in brands.split(',') if b.strip().isdigit()]
            
            all_subcategory_ids = set(subcategory_ids)
            for cid in subcategory_ids:
                subcats = self.get_all_subcategories(cid)
                all_subcategory_ids.update([c.id for c in subcats])

            queryset = queryset.filter(category__in=all_subcategory_ids)

        if keyword:
            if type_search_keyword == 'exact':
                queryset = queryset.filter(text_search=keyword)
            elif type_search_keyword == 'contains':
                queryset = queryset.filter(text_search__icontains=keyword)
            elif type_search_keyword == 'startswith':
                queryset = queryset.filter(text_search__istartswith=keyword)
            elif type_search_keyword == 'endswith':
                queryset = queryset.filter(text_search__iendswith=keyword)
            else:
                raise ValidationError("Require keyword type search in ['exact', 'contains', 'startswith', 'endswith']")

        if category_name: 
            try:
                category_objs = Category.objects.filter(name__icontains=category_name)
                all_ids = set([cat_obj.id for cat_obj in category_objs])
                print("all_ids", all_ids)
                for cat_obj in category_objs: 
                    subcats = self.get_all_subcategories(cat_obj.id)
                    all_ids.update([c.id for c in subcats])
                print("all_ids", all_ids)
                queryset = queryset.filter(category__in=all_ids)
            except Category.DoesNotExist:
                print("category_name is not found in database")

        if brand_name: 
            try:
                brand_obj = Brand.objects.get(name__iexact=brand_name)
                queryset = queryset.filter(brand=brand_obj.id)
            except Brand.DoesNotExist:
                print("brand_name is not found in database")

        if price:
            price = price.strip()
            if price.startswith('<'):
                try:
                    threshold = int(price[1:].strip())
                    queryset = queryset.filter(min_price__lt=threshold)
                except ValueError:
                    raise ValidationError("Invalid price format. Expected format: '< number'")
            elif price.startswith('>'):
                try:
                    threshold = int(price[1:].strip())
                    queryset = queryset.filter(max_price__gt=threshold)
                except ValueError:
                    raise ValidationError("Invalid price format. Expected format: '> number'")
            else:
                try:
                    parts = price.split('->')
                    if len(parts) == 2:
                        min_val, max_val = int(parts[0]), int(parts[1])
                        queryset = queryset.filter(
                            min_price__gte=min_val,
                            max_price__lte=max_val
                        )
                    else:
                        raise ValidationError("Invalid price range. Expected format: 'min->max'")
                except ValueError:
                    raise ValidationError("Invalid price format. Expected numbers.")
        
        if sort_by:
            if sort_by == 'bestseller':
                queryset = queryset.order_by('-sold_per_month')
            elif sort_by == 'lowtohigh':
                queryset = queryset.order_by('min_price')
            elif sort_by == 'hightolow':
                queryset = queryset.order_by('-max_price')
            else:
                raise ValidationError("Require sort_by in ['bestseller', 'lowtohigh', 'hightolow']")

        return queryset

    def get_all_subcategories(self, parent_category):
        subcategories = Category.objects.filter(parent=parent_category)
        all_subcategories = list(subcategories)
        for subcategory in subcategories:
            all_subcategories.extend(self.get_all_subcategories(subcategory))
        return all_subcategories
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProductSearchViewOR(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminPermission]
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        description = self.request.query_params.get('description', None)
        category = self.request.query_params.get('category', None)
        brand = self.request.query_params.get('brand', None)
        
        queryset = Product.objects.all().order_by('id')
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value)

        filters = Q()

        if name:
            type_search_name = self.request.query_params.get('type_search_name', 'exact')
            if type_search_name == 'exact':
                filters |= Q(name=name)
            elif type_search_name == 'contains':
                filters |= Q(name__icontains=name)
            elif type_search_name == 'startswith':
                filters |= Q(name__istartswith=name)
            elif type_search_name == 'endswith':
                filters |= Q(name__iendswith=name)
            else:
                raise ValidationError("Require name type search in ['exact', 'contains', 'startswith', 'endswith']")

        if description:
            type_search_description = self.request.query_params.get('type_search_description', 'exact')
            if type_search_description == 'exact':
                filters |= Q(description=description)
            elif type_search_description == 'contains':
                filters |= Q(description__icontains=description)
            elif type_search_description == 'startswith':
                filters |= Q(description__istartswith=description)
            elif type_search_description == 'endswith':
                filters |= Q(description__iendswith=description)
            else:
                raise ValidationError("Require description type search in ['exact', 'contains', 'startswith', 'endswith']")
        
        if category:
            type_search_category = self.request.query_params.get('type_search_category', 'exact')
            if type_search_category == 'exact':
                filters |= Q(category=category)
            elif type_search_category == 'contains':
                filters |= Q(category__icontains=category)
            elif type_search_category == 'startswith':
                filters |= Q(category__istartswith=category)
            elif type_search_category == 'endswith':
                filters |= Q(category__iendswith=category)
            else:
                raise ValidationError("Require category type search in ['exact', 'contains', 'startswith', 'endswith']")
    
        if brand:
            type_search_brand = self.request.query_params.get('type_search_brand', 'exact')
            if type_search_brand == 'exact':
                filters |= Q(brand=brand)
            elif type_search_brand == 'contains':
                filters |= Q(brand__icontains=brand)
            elif type_search_brand == 'startswith':
                filters |= Q(brand__istartswith=brand)
            elif type_search_brand == 'endswith':
                filters |= Q(brand__iendswith=brand)
            else:
                raise ValidationError("Require brand type search in ['exact', 'contains', 'startswith', 'endswith']")
        
        queryset = queryset.filter(filters)

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    serializer_class = ProductSerializer
    permission_classes = [IsAdminPermission]
    
##--------------Catogery--------------##
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()

    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CategoryUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return CategorySerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsCategorySerializer
        return CategorySerializer

    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Category._meta.get_fields()]:
                if param == 'parent': 
                    if value == 'null':
                        value = None 
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    def list(self, request, *args, **kwargs):
        print("category list")
        queryset = self.filter_queryset(self.get_queryset())

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = CategorySerializerOutput(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = CategorySerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        print("category retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=CategoryUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("category create")
        data = request.data.copy()
        parent_id = request.data.get('parent_id', None)
        print("parent_id", parent_id)
        if parent_id!=None: 
            try:
                parent = Category.objects.get(id=parent_id)
                data['parent'] = parent.id
                print("vao day")
            except Category.DoesNotExist:
                return Response({'detail': 'Category not found'}, status=status.HTTP_403_FORBIDDEN) 
        category = CategorySerializer(data=data)
        if category.is_valid():
            category.save()
        else:
            return Response(
                {"detail": "Category is invalid",  "errors": category.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"category": category.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        parent_id = request.data.get('parent_id', None)
        print("parent_id", parent_id)
        if parent_id!=None: 
            try:
                parent = Category.objects.get(id=parent_id)
                data['parent'] = parent.id
                print("vao day")
            except Category.DoesNotExist:
                return Response({'detail': 'Category not found'}, status=status.HTTP_403_FORBIDDEN) 
        
        category = CategorySerializer(instance, data=data, partial=partial)
        category.is_valid(raise_exception=True)
        category.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        print("category partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        parent_id = request.data.get('parent_id', None)
        print("parent_id", parent_id)
        if parent_id!=None: 
            try:
                parent = Category.objects.get(id=parent_id)
                data['parent'] = parent.id
                print("vao day")
            except Category.DoesNotExist:
                return Response({'detail': 'Category not found'}, status=status.HTTP_403_FORBIDDEN) 
            
        category = CategorySerializer(instance, data=data, partial=partial)
        category.is_valid(raise_exception=True)
        category.save()

        return Response(category.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("Category destroy")
        pk = kwargs.get('pk')
        
        try:
            instance = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        instance.delete()
        return Response({'detail': 'Category deleted successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("Category soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Category already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        
        recursive_soft_delete(instance)
        return Response({'detail': 'Category and its subcategories soft deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(responses={200: ResponseSerializer})
    def multiple_delete(self, request):
        print("Category multiple_delete")
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'detail': 'No category IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        categories = Category.objects.filter(id__in=ids)

        if not categories.exists():
            return Response({'detail': 'No categories found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        for category in categories:
            recursive_soft_delete(category)

        return Response({'detail': 'Categories and their subcategories soft deleted successfully'}, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(responses={200: ResponseSerializer})
    def multiple_destroy(self, request):
        print("Category multiple_destroy")
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'detail': 'No category IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        categories = Category.objects.filter(id__in=ids)

        if not categories.exists():
            return Response({'detail': 'No categories found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        for category in categories:
            category.delete()
            print(f"Deleted: {category.name}")

        return Response({'detail': 'Categories deleted successfully'}, status=status.HTTP_200_OK)
    
##-------------Brand----------------##
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()

    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['retrieve', 'list']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return BrandUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return BrandSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsBrandSerializer
        return BrandSerializer

    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Brand._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    def list(self, request, *args, **kwargs):
        print("brand list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = BrandSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BrandSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        print("brand retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=BrandSerializer,
        responses={200: BrandSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"brand": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(
            {"detail": "Brand is invalid", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = BrandUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, partial=True, *args, **kwargs)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'detail': 'Brand deleted successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("Brand soft_delete")
        try:
            instance = Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return Response({'detail': 'Brand not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Brand already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)

        soft_delete_brand(instance)
        return Response({'detail': 'Brand and its products soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("Brand multiple soft_delete")
        ids = request.data.get('ids', [])

        if not ids:
            return Response({'detail': 'No IDs provided.'}, status=status.HTTP_400_BAD_REQUEST)

        brands = Brand.objects.filter(id__in=ids)

        if not brands.exists():
            return Response({'detail': 'No matching brands found.'}, status=status.HTTP_404_NOT_FOUND)

        for brand in brands:
            soft_delete_brand(brand)

        return Response({'detail': 'Selected brands and their products soft deleted successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': 'No brand IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        brands = Brand.objects.filter(id__in=ids)
        if not brands.exists():
            return Response({'detail': 'No brands found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        for brand in brands:
            brand.delete()

        return Response({'detail': 'Brands deleted successfully'}, status=status.HTTP_200_OK)

##---------------SubProduct---------------##
class SubProductViewSet(viewsets.ModelViewSet):
    queryset = SubProduct.objects.all().order_by('id')
    serializer_class = SubProductSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()

    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return SubProductUpdateSerializer
        elif self.action in ['list']:
            return SubProductSerializer
        elif self.action in ['retrieve']:
            return SubProductSerializerForAdmin
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsSubProductSerializer
        return SubProductSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in SubProduct._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("subProduct list")
        queryset = self.filter_queryset(self.get_queryset())

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = SubProductSerializerOutput(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = SubProductSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("subProduct retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=SubProductUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("subProduct create")
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        # Xử lý product_id
        product_id = request.data.get('product_id', None)
        print("product_id", product_id)
        data_productSubProduct = {}
        if product_id!=None: 
            try:
                product = Product.objects.get(id=product_id)
                data_productSubProduct['product'] = product.id
                print("vao day")
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'product_id not found'}, status=status.HTTP_404_NOT_FOUND)
            
        subProduct = SubProductSerializer(data=data)

        if subProduct.is_valid():
            subProduct.save()
            print("subProduct.data.get('id')", subProduct.data.get('id'))
            data_productSubProduct['sub_product'] = subProduct.data.get('id')
            productSubProduct = ProductSubProductSerializer(data=data_productSubProduct)
            if productSubProduct.is_valid():
                productSubProduct.save()
            else: 
                return Response(
                    {"detail": "ProductSubProduct is invalid",  "errors": productSubProduct.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"detail": "SubProduct is invalid",  "errors": subProduct.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"subProduct": subProduct.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        # Xử lý product_id
        product_id = request.data.get('product_id', None)
        print("product_id", product_id)
        data_productSubProduct = {}
        if product_id!=None: 
            try:
                product = Product.objects.get(id=product_id)
                data_productSubProduct['product'] = product.id
                print("vao day")
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        product_subproducts = instance.products.select_related('product')
        if len(product_subproducts) == 1: 
            product_subproduct = product_subproducts[0]
            productSubProduct = ProductSubProductSerializer(product_subproduct, data=data_productSubProduct, partial=partial)
            productSubProduct.is_valid(raise_exception=True)
            productSubProduct.save()


        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        subProduct = SubProductSerializer(instance, data=data, partial=partial)
        subProduct.is_valid(raise_exception=True)
        subProduct.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("subProduct partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        # Xử lý product_id
        product_id = request.data.get('product_id', None)
        print("product_id", product_id)
        data_productSubProduct = {}
        if product_id!=None: 
            try:
                product = Product.objects.get(id=product_id)
                data_productSubProduct['product'] = product.id
                print("vao day")
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        product_subproducts = instance.product.select_related('product')
        if len(product_subproducts) == 1: 
            product_subproduct = product_subproducts[0]
            productSubProduct = ProductSubProductSerializer(product_subproduct, data=data_productSubProduct, partial=partial)
            productSubProduct.is_valid(raise_exception=True)
            productSubProduct.save()


        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        subProduct = SubProductSerializer(instance, data=data, partial=partial)
        subProduct.is_valid(raise_exception=True)
        subProduct.save()

        return Response(subProduct.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("subProduct destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = SubProduct.objects.get(id=pk)
        except SubProduct.DoesNotExist:
            return Response({'detail': 'SubProduct not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'SubProduct deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("subProduct soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'SubProduct already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()

        product_subproducts = instance.product.select_related('product')
        if len(product_subproducts) == 1: 
            product_subproduct = product_subproducts[0]
            if product_subproduct.status_enum != StatusEnum.DELETED.value:
                product_subproduct.status_enum = StatusEnum.DELETED.value
                product_subproduct.save()
        return Response({'detail': 'SubProduct soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("subProduct multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No subProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        subProducts = SubProduct.objects.filter(id__in=ids)
        if not subProducts.exists():
            return Response({'message': 'No subProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        deleted_count = 0
        already_deleted_ids = []

        for subProduct in subProducts:
            if subProduct.status_enum == StatusEnum.DELETED.value:
                already_deleted_ids.append(subProduct.id)
                continue

            subProduct.status_enum = StatusEnum.DELETED.value
            subProduct.save()
            deleted_count += 1

            product_subproducts = subProduct.products.select_related('product')
            if len(product_subproducts) == 1:
                product_subproduct = product_subproducts[0]
                if product_subproduct.status_enum != StatusEnum.DELETED.value:
                    product_subproduct.status_enum = StatusEnum.DELETED.value
                    product_subproduct.save()

        response_data = {
            'message': f'SubProducts soft deleted: {deleted_count}',
            'already_deleted_ids': already_deleted_ids
        }
        return Response(response_data, status=status.HTTP_200_OK)

    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('subProduct multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No subProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        subProducts = SubProduct.objects.filter(id__in=ids) 
        if not subProducts.exists():
            return Response({'message': 'No subProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for subProduct in subProducts:
            subProduct.delete()
        return Response({'message': 'SubProducts destroy successfully'}, status=status.HTTP_200_OK)

##---------------ProductSubProduct---------------##
class ProductSubProductViewSet(viewsets.ModelViewSet):
    queryset = ProductSubProduct.objects.all()
    serializer_class = ProductSubProductSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) == 'create':
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action == 'create':
            return [] 
        elif self.action == 'list':
            print("list check", [IsCustomerPermission() or IsAdminPermission()])
            return [(IsCustomerPermission | IsAdminPermission)()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'soft_delete']:
            return [(IsAuthenticatedPermission | IsAdminPermission)()]
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]
        elif self.action == 'me':
            return [IsAuthenticatedPermission()]
        return [IsAuthenticatedPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProductSubProductUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return ProductSubProductSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsProductSubProductSerializer
        return ProductSubProductSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in ProductSubProduct._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("productsubproduct list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSubProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSubProductSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("productsubproduct retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=ProductSubProductSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("productsubproduct create")
        return Response({"message": "Method not allow"}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        productsubproduct = ProductSubProductSerializer(instance, data=data, partial=partial)
        productsubproduct.is_valid(raise_exception=True)
        productsubproduct.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("productsubproduct partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)
        # serializer = self.get_serializer(instance, data=data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        productsubproduct = ProductSubProductSerializer(instance, data=data, partial=partial)
        productsubproduct.is_valid(raise_exception=True)
        productsubproduct.save()

        return Response(productsubproduct.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("productsubproduct destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = ProductSubProduct.objects.get(id=pk)
        except ProductSubProduct.DoesNotExist:
            return Response({'detail': 'ProductSubProduct not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'ProductSubProduct deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("productsubproduct soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'ProductSubProduct already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'ProductSubProduct soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("productsubproduct multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No productsubproduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        productsubproducts = ProductSubProduct.objects.filter(id__in=ids) 
        if not productsubproducts.exists():
            return Response({'message': 'No productsubproducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        productsubproducts.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'ProductSubProducts soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('productsubproduct multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No productsubproduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        productsubproducts = ProductSubProduct.objects.filter(id__in=ids) 
        if not productsubproducts.exists():
            return Response({'message': 'No productsubproducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for productsubproduct in productsubproducts:
            productsubproduct.delete()
        return Response({'message': 'ProductSubProducts destroy successfully'}, status=status.HTTP_200_OK)
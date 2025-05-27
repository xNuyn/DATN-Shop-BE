from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, status
from compare.serializers import CompareProductSerializer, CompareProductSerializerOutput, CompareProductUpdateSerializer, IdsCompareProductSerializer
from app.serializers import ResponseSerializer
from compare.models import CompareProduct
from app.models import StatusEnum
from products.models import SubProduct, ProductSubProduct, Product, Category
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission
from drf_yasg.utils import swagger_auto_schema

def get_root_category(category):
    while category.parent is not None:
        category = category.parent
    return category

class CompareProductViewSet(viewsets.ModelViewSet):
    queryset = CompareProduct.objects.all().order_by('id')
    serializer_class = CompareProductSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy', 'my_compareProduct']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CompareProductUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return CompareProductSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsCompareProductSerializer
        return CompareProductSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in CompareProduct._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
        print("compareProduct list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CompareProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompareProductSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("compareProduct retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=CompareProductUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("compareProduct create")
        data = request.data.copy()
        user = request.user
        user_id = user.id
        data['user'] = user_id

        sub_product_id = data.get('sub_product_id')
        if not sub_product_id:
            return Response({'detail': 'Missing sub_product_id'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Kiểm tra sub_product tồn tại
        try:
            sub_product = SubProduct.objects.get(id=sub_product_id)
        except SubProduct.DoesNotExist:
            return Response({'detail': 'SubProduct not found'}, status=status.HTTP_404_NOT_FOUND)

        # 2. Lấy Product gốc của sub_product
        try:
            product = ProductSubProduct.objects.get(sub_product=sub_product).product
        except ProductSubProduct.DoesNotExist:
            return Response({'detail': 'Product mapping not found for this SubProduct'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Lấy category gốc của sản phẩm
        root_category = get_root_category(product.category)

        # 4. Lấy danh sách các CompareProduct đã tạo bởi user
        existing_compare_items = CompareProduct.objects.filter(user=user, status_enum=StatusEnum.ACTIVE)

        # 5. Kiểm tra số lượng sản phẩm đã được so sánh
        if existing_compare_items.count() >= 6:
            return Response({"detail": "Chỉ có thể so sánh tối đa 6 sản phẩm."}, status=status.HTTP_400_BAD_REQUEST)

        # 6. Kiểm tra cùng danh mục gốc
        for item in existing_compare_items:
            try:
                existing_product = ProductSubProduct.objects.get(sub_product=item.sub_product).product
                existing_root_category = get_root_category(existing_product.category)
            except ProductSubProduct.DoesNotExist:
                continue  # bỏ qua nếu dữ liệu không khớp

            if existing_root_category.id != root_category.id:
                return Response({"detail": "Tất cả sản phẩm so sánh phải thuộc cùng danh mục gốc."},
                                status=status.HTTP_400_BAD_REQUEST)

        # 7. Tạo CompareProduct mới
        data['sub_product'] = sub_product.id
        compare_serializer = CompareProductSerializer(data=data)
        if compare_serializer.is_valid():
            compare_serializer.save()
            return Response({"compareProduct": compare_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "CompareProduct is invalid", "errors": compare_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id: 
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        compareProduct = CompareProductSerializer(instance, data=data, partial=partial)
        compareProduct.is_valid(raise_exception=True)
        compareProduct.save()

        compareProductModel = CompareProduct.objects.get(id=compareProduct.data.get('id'))

        compareProductOutput = CompareProductSerializerOutput(compareProductModel)
    
        return Response(compareProductOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("compareProduct partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        compareProduct = CompareProductSerializer(instance, data=data, partial=partial)
        compareProduct.is_valid(raise_exception=True)
        compareProduct.save()

        compareProductModel = CompareProduct.objects.get(id=compareProduct.data.get('id'))

        compareProductOutput = CompareProductSerializerOutput(compareProductModel)
    
        return Response(compareProductOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("compareProduct destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = CompareProduct.objects.get(id=pk)
        except CompareProduct.DoesNotExist:
            return Response({'detail': 'CompareProduct not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'CompareProduct deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("compareProduct soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'CompareProduct already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'CompareProduct soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("compareProduct multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No compareProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        compareProducts = CompareProduct.objects.filter(id__in=ids) 
        if not compareProducts.exists():
            return Response({'message': 'No compareProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in compareProducts: 
            if user_id != instance.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        compareProducts.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'CompareProducts soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('compareProduct multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No compareProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        compareProducts = CompareProduct.objects.filter(id__in=ids) 
        if not compareProducts.exists():
            return Response({'message': 'No compareProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for compareProduct in compareProducts:
            if user_id != compareProduct.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            compareProduct.delete()

        return Response({'message': 'CompareProducts destroy successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['get'], url_path='my-compareproduct')
    @swagger_auto_schema(
        responses={200: CompareProductSerializerOutput}
    )
    def my_compareProduct(self, request):
        print('compareProduct my_compareProduct')

        user_id = request.user.id
        print("user_id", user_id)
        try:
            compareProducts = CompareProduct.objects.filter(user=user_id)
        except CompareProduct.DoesNotExist: 
            return Response({'detail': 'No item found in my compareProduct'}, status=status.HTTP_403_FORBIDDEN) 
        page = self.paginate_queryset(compareProducts)
        if page is not None:
            compareProductOutput = CompareProductSerializerOutput(page, many=True)
            return self.get_paginated_response(compareProductOutput.data)

        return Response(compareProductOutput.data, status=status.HTTP_200_OK)
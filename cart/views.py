from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, status
from cart.serializers import (
    CartSerializer, CartSerializerOutput, CartUpdateSerializer, IdsCartSerializer,
    WishlistSerializer, WishlistSerializerOutput, WishlistUpdateSerializer, IdsWishlistSerializer)
from app.serializers import ResponseSerializer
from cart.models import Cart, Wishlist
from app.models import StatusEnum
from products.models import SubProduct
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission
from drf_yasg.utils import swagger_auto_schema

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().order_by('id')
    serializer_class = CartSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy', 'my_cart']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CartUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return CartSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsCartSerializer
        return CartSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Cart._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("cart list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CartSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CartSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("cart retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=CartUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("cart create")
        data = request.data.copy()
        user_id = request.user.id
        data['user'] = user_id
        sub_product_id = request.data.get('sub_product_id', None)
        print("sub_product_id", sub_product_id)
        if sub_product_id!=None: 
            try:
                sub_product = SubProduct.objects.get(id=sub_product_id)
                data['sub_product'] = sub_product.id
            except SubProduct.DoesNotExist:
                return Response({'detail': 'SubProduct not found'}, status=status.HTTP_403_FORBIDDEN) 
        cart = CartSerializer(data=data)
        if cart.is_valid():
            cart.save()
        else:
            return Response(
                {"detail": "Cart is invalid",  "errors": cart.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"cart": cart.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id: 
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        cart = CartSerializer(instance, data=data, partial=partial)
        cart.is_valid(raise_exception=True)
        cart.save()

        cartModel = Cart.objects.get(id=cart.data.get('id'))

        cartOutput = CartSerializerOutput(cartModel)
    
        return Response(cartOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("cart partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        cart = CartSerializer(instance, data=data, partial=partial)
        cart.is_valid(raise_exception=True)
        cart.save()

        cartModel = Cart.objects.get(id=cart.data.get('id'))

        cartOutput = CartSerializerOutput(cartModel)
    
        return Response(cartOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("cart destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Cart.objects.get(id=pk)
        except Cart.DoesNotExist:
            return Response({'detail': 'Cart not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'Cart deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("cart soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Cart already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'Cart soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("cart multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No cart IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        carts = Cart.objects.filter(id__in=ids) 
        if not carts.exists():
            return Response({'message': 'No carts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in carts: 
            if user_id != instance.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        carts.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Carts soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('cart multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No cart IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        carts = Cart.objects.filter(id__in=ids) 
        if not carts.exists():
            return Response({'message': 'No carts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for cart in carts:
            if user_id != cart.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            cart.delete()

        return Response({'message': 'Carts destroy successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['get'], url_path='my-cart')
    @swagger_auto_schema(
        responses={200: CartSerializerOutput}
    )
    def my_cart(self, request):
        print('cart my_cart')

        user_id = request.user.id
        print("user_id", user_id)
        try:
            carts = Cart.objects.filter(user=user_id)
        except Cart.DoesNotExist: 
            return Response({'detail': 'No item found in my cart'}, status=status.HTTP_403_FORBIDDEN) 
        page = self.paginate_queryset(carts)
        if page is not None:
            cartOutput = CartSerializerOutput(page, many=True)
            return self.get_paginated_response(cartOutput.data)

        return Response(cartOutput.data, status=status.HTTP_200_OK)

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all().order_by('id')
    serializer_class = WishlistSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy', 'my_wishlist']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()]
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return WishlistUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return WishlistSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsWishlistSerializer
        return WishlistSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Wishlist._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("wishlist list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WishlistSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WishlistSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("wishlist retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=WishlistUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("wishlist create")
        data = request.data.copy()
        user_id = request.user.id
        data['user'] = user_id
        sub_product_id = request.data.get('sub_product_id', None)
        print("sub_product_id", sub_product_id)
        if sub_product_id!=None: 
            try:
                sub_product = SubProduct.objects.get(id=sub_product_id)
                data['sub_product'] = sub_product.id
            except SubProduct.DoesNotExist:
                return Response({'detail': 'SubProduct not found'}, status=status.HTTP_403_FORBIDDEN) 
        wishlist = WishlistSerializer(data=data)
        if wishlist.is_valid():
            wishlist.save()
        else:
            return Response(
                {"detail": "Wishlist is invalid",  "errors": wishlist.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"wishlist": wishlist.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id: 
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        wishlist = WishlistSerializer(instance, data=data, partial=partial)
        wishlist.is_valid(raise_exception=True)
        wishlist.save()

        wishlistModel = Wishlist.objects.get(id=wishlist.data.get('id'))

        wishlistOutput = WishlistSerializerOutput(wishlistModel)
    
        return Response(wishlistOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("wishlist partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        wishlist = WishlistSerializer(instance, data=data, partial=partial)
        wishlist.is_valid(raise_exception=True)
        wishlist.save()

        wishlistModel = Wishlist.objects.get(id=wishlist.data.get('id'))

        wishlistOutput = WishlistSerializerOutput(wishlistModel)
    
        return Response(wishlistOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("wishlist destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Wishlist.objects.get(id=pk)
        except Wishlist.DoesNotExist:
            return Response({'detail': 'Wishlist not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'Wishlist deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("wishlist soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Wishlist already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'Wishlist soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("wishlist multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No wishlist IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        wishlists = Wishlist.objects.filter(id__in=ids) 
        if not wishlists.exists():
            return Response({'message': 'No wishlists found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in wishlists: 
            if user_id != instance.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        wishlists.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Wishlists soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('wishlist multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No wishlist IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        wishlists = Wishlist.objects.filter(id__in=ids) 
        if not wishlists.exists():
            return Response({'message': 'No wishlists found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for wishlist in wishlists:
            if user_id != wishlist.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            wishlist.delete()

        return Response({'message': 'Wishlists destroy successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['get'], url_path='my-wishlist')
    @swagger_auto_schema(
        responses={200: WishlistSerializerOutput}
    )
    def my_wishlist(self, request):
        print('wishlist my_wishlist')

        user_id = request.user.id
        print("user_id", user_id)
        try:
            wishlists = Wishlist.objects.filter(user=user_id)
        except Wishlist.DoesNotExist: 
            return Response({'detail': 'No item found in my wishlist'}, status=status.HTTP_403_FORBIDDEN) 
        page = self.paginate_queryset(wishlists)
        if page is not None:
            wishlistOutput = CartSerializerOutput(page, many=True)
            return self.get_paginated_response(wishlistOutput.data)

        return Response(wishlistOutput.data, status=status.HTTP_200_OK)
    

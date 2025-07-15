from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from orders.serializers import OrderSerializer, OrderSerializerOutput, OrderUpdateSerializer, IdsOrderSerializer, OrderDetailSerializer, OrderDetailSerializerOutput, OrderDetailUpdateSerializer, IdsOrderDetailSerializer
from app.serializers import ResponseSerializer
from orders.models import Order, OrderDetail, StatusEnum
from products.models import SubProduct
import requests
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission
from drf_yasg.utils import swagger_auto_schema

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('id')
    serializer_class = OrderSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'my_orders']: 
            return [(IsCustomerPermission)()]
        if self.action in ['retrieve', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy']: 
            return [(IsCustomerPermission | IsAdminPermission)()]
        elif self.action in ['list']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return OrderSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsOrderSerializer
        return OrderSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Order._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs).order_by("-created_at")
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
        print("order list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("order retrieve")
        # user_id = request.user.id
        instance = self.get_object()
        # if user_id != instance.user.id:
        #     return Response({
        #         "detail": "You do not have permission to perform this action."
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderSerializerOutput(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=OrderUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("order create")
        data = request.data.copy()
        user_id = request.user.id
        data['user'] = user_id
        
        order = OrderSerializer(data=data)
        if order.is_valid():
            order.save()
        else:
            return Response(
                {"detail": "Order is invalid", "errors": order.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"order": order.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id: 
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        status_value = data.get('status', None)
        if status_value != None and request.user.role != 'admin':
            return Response({
                "detail": "You do not have permission to change the status of this order."
            }, status=status.HTTP_403_FORBIDDEN)

        order = OrderSerializer(instance, data=data, partial=partial)
        order.is_valid(raise_exception=True)
        order.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("order partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id and request.user.role!='admin':
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        status_value = data.get('status', None)
        if status_value != None and status_value!='canceled' and request.user.role != 'admin':
            return Response({
                "detail": "You do not have permission to change the status of this order."
            }, status=status.HTTP_403_FORBIDDEN)

        order = OrderSerializer(instance, data=data, partial=partial)
        order.is_valid(raise_exception=True)
        order.save()

        return Response(order.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("order destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response({'message': 'Order deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("order soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Order already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'Order soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("order multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No order IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        orders = Order.objects.filter(id__in=ids) 
        if not orders.exists():
            return Response({'message': 'No orders found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for order in orders:
            if user_id != order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            
        orders.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Orders soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('order multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No order IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        orders = Order.objects.filter(id__in=ids) 
        if not orders.exists():
            return Response({'message': 'No orders found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for order in orders:
            if user_id != order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action with order ID: {}".format(order.id)
                }, status=status.HTTP_403_FORBIDDEN)

        for order in orders:
            order.delete()
        return Response({'message': 'Orders destroy successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-orders')
    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)}
    )
    def my_orders(self, request):
        print("order my_orders")
        user_id = request.user.id
        queryset = self.queryset.filter(user_id=user_id, status_enum=StatusEnum.ACTIVE.value).order_by("-created_at")
        
        if not queryset.exists():
            return Response({'detail': 'No orders found for this user'}, status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all().order_by('id')
    serializer_class = OrderDetailSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy', 'my_order_details']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return OrderDetailUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return OrderDetailSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsOrderDetailSerializer
        return OrderDetailSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in OrderDetail._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
        print("orderDetail list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderDetailSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderDetailSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("orderDetail retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=OrderDetailUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("orderDetail create")
        data = request.data.copy()
        user_id = request.user.id
        data['user'] = user_id

        order_id = request.data.get('order_id', None)
        if order_id is None:
            return Response({'detail': 'Order ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check user has permission to create order detail
        try:
            order = Order.objects.get(id=order_id, user_id=user_id, status_enum=StatusEnum.ACTIVE.value)
            data['order'] = order.id
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found or you do not have permission to access it'}, status=status.HTTP_403_FORBIDDEN)
        
        # check sub_product_id is valid
        if 'sub_product_id' not in request.data:
            return Response({'detail': 'SubProduct ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        sub_product_id = request.data.get('sub_product_id', None)
        print("sub_product_id", sub_product_id)
        if sub_product_id!=None: 
            try:
                sub_product = SubProduct.objects.get(id=sub_product_id)
                data['sub_product'] = sub_product.id
            except SubProduct.DoesNotExist:
                return Response({'detail': 'SubProduct not found'}, status=status.HTTP_403_FORBIDDEN) 
        orderDetail = OrderDetailSerializer(data=data)
        if orderDetail.is_valid():
            orderDetail.save()
        else:
            return Response(
                {"detail": "OrderDetail is invalid",  "errors": orderDetail.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"orderDetail": orderDetail.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        orderDetail = OrderDetailSerializer(instance, data=data, partial=partial)
        orderDetail.is_valid(raise_exception=True)
        orderDetail.save()

        orderDetailModel = OrderDetail.objects.get(id=orderDetail.data.get('id'))

        orderDetailOutput = OrderDetailSerializerOutput(orderDetailModel)
    
        return Response(orderDetailOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("orderDetail partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        orderDetail = OrderDetailSerializer(instance, data=data, partial=partial)
        orderDetail.is_valid(raise_exception=True)
        orderDetail.save()

        orderDetailModel = OrderDetail.objects.get(id=orderDetail.data.get('id'))

        orderDetailOutput = OrderDetailSerializerOutput(orderDetailModel)
    
        return Response(orderDetailOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("orderDetail destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = OrderDetail.objects.get(id=pk)
        except OrderDetail.DoesNotExist:
            return Response({'detail': 'OrderDetail not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'OrderDetail deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("orderDetail soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'OrderDetail already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'OrderDetail soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("orderDetail multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No orderDetail IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        orderDetails = OrderDetail.objects.filter(id__in=ids) 
        if not orderDetails.exists():
            return Response({'message': 'No orderDetails found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in orderDetails: 
            if user_id != instance.order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        orderDetails.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'OrderDetails soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('orderDetail multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No orderDetail IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        orderDetails = OrderDetail.objects.filter(id__in=ids) 
        if not orderDetails.exists():
            return Response({'message': 'No orderDetails found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for orderDetail in orderDetails:
            if user_id != orderDetail.order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            orderDetail.delete()

        return Response({'message': 'OrderDetails destroy successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='my-order-details')
    @swagger_auto_schema(
        responses={200: OrderDetailSerializerOutput(many=True)}
    )
    def my_order_details(self, request):
        print('orderDetail my_cart')

        user_id = request.user.id
        queryset = self.queryset.filter(order__user_id=user_id, status_enum=StatusEnum.ACTIVE.value)
        if not queryset.exists():
            return Response({'detail': 'No order details found for this user'}, status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderDetailSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderDetailSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
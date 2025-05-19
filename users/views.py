from django.shortcuts import render
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Value, BooleanField
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from users.serializers import UserSerializer, UserSerializerOutput, UserUpdateSerializer, IdsUserSerializer, ResponseSerializer
from users.models import User, StatusEnum
import requests
from random import sample
import json
from rest_framework.decorators import action
from rest_framework.views import APIView
from datetime import datetime
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
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
            return [IsCustomerPermission() or IsAdminPermission()]  # Chỉ admin mới được xem danh sách user
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'soft_delete']:
            return [IsAuthenticatedPermission() or IsAdminPermission()]  # Chính mình hoặc admin
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()] # Chỉ admin mới được phép xóa nhiều user
        elif self.action == 'me':
            return [IsAuthenticatedPermission()]
        return [IsAuthenticatedPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return UserSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsUserSerializer
        return UserSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in User._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("user list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("user retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("user create")
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

        # serializer = self.get_serializer(instance, data=data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        user = UserSerializer(instance, data=data, partial=partial)
        user.is_valid(raise_exception=True)
        user.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("user partial_update")
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
        user = UserSerializer(instance, data=data, partial=partial)
        user.is_valid(raise_exception=True)
        user.save()

        return Response(user.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("user destroy")
        try:
            instance = self.get_object()
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'User deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("user soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'User already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'User soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("user multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No user IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids) 
        if not users.exists():
            return Response({'message': 'No users found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        users.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Users soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('user multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No user IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids) 
        if not users.exists():
            return Response({'message': 'No users found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for user in users:
            user.delete()
        return Response({'message': 'Users destroy successfully'}, status=status.HTTP_200_OK)
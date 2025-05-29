from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'role')

class UserSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'user_name', 'full_name', 'email', 'avatar', 'phone', 'address', 'region', 'address_billing', 'zip_code', 'note')
        read_only_fields = ('id', 'created_at', 'role')
        
class UserUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields = ('full_name', 'user_name', 'email', 'phone', 'address', 'region', 'address_billing', 'zip_code', 'note', 'image')
        read_only_fields = ('id', 'created_at', 'role')
    
class IdsUserSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
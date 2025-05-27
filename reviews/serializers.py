from rest_framework import serializers
from .models import Review
from products.serializers import *

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ReviewSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerOutput()
    class Meta:
        model = Review
        fields = ('id', 'user', 'sub_product', 'rating', 'comment')
        
class ReviewUpdateSerializer(serializers.ModelSerializer):
    sub_product_id = serializers.IntegerField(required=False)
    class Meta:
        model = Review
        fields = ('sub_product_id', 'rating', 'comment')
    
class IdsReviewSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
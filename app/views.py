# upload/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UploadImageSerializer
import cloudinary.uploader
from rest_framework.decorators import authentication_classes
from django.conf import settings

cloudinary.config( 
  cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME'], 
  api_key = settings.CLOUDINARY_STORAGE['API_KEY'], 
  api_secret = settings.CLOUDINARY_STORAGE['API_SECRET'] 
)

@authentication_classes([])
class UploadImageView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            result = cloudinary.uploader.upload(image)
            image_url = result.get("secure_url")
            return Response({"image_url": image_url}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import jwt
from rest_framework import authentication, exceptions
from django.conf import settings
from users.models import User

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        print('JWTAuthentication')
        auth_data = authentication.get_authorization_header(request)
        if not auth_data:
            print('No token found')
            return
        access_token = auth_data.decode('utf-8')
        if 'Bearer' in access_token:
            access_token = access_token.split(' ')[1]
        try: 
            payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms='HS256')
            user = User.objects.get(user_name=payload['username'])
            request.user = user
            request.access_token = access_token
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        except jwt.DecodeError as identifier:
            raise exceptions.AuthenticationFailed('Your token is invalid, login')
        except jwt.ExpiredSignatureError as identifier:
            raise exceptions.AuthenticationFailed('Your token is expired, login')
        return (user, None) 
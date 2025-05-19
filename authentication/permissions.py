from rest_framework import permissions

class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print('IsCustomerPermission')
        print("request.user.role", request.user.role)
        print(request.user.role == 'customer')
        return request.user and str(request.user)!='AnonymousUser' and request.user.role == 'customer'

class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print('IsAdminPermission')
        print("request.user", request.user)
        return request.user and str(request.user)!='AnonymousUser' and request.user.role == 'admin'

# là chính mình
class IsAuthenticatedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print('IsAuthenticatedPermission')
        pk = request.parser_context['kwargs'].get('pk')
        return request.user and str(request.user)!='AnonymousUser' and (str(pk) == str(request.user.id))
from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost","192.168.231.205", "3148-2402-9d80-44b-6919-199-875f-9286-3ed1.ngrok-free.app"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("PROD_DB_NAME", "prod_db"),
        "USER": os.getenv("PROD_DB_USER", "root"),
        "PASSWORD": os.getenv("PROD_DB_PASSWORD", "nguyen070302"),
        "HOST": os.getenv("PROD_DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("PROD_DB_PORT", "3306"),
    }
}

# Cấu hình bảo mật cho production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
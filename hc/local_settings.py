DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hc',
        'USER': 'postgres',
        'PASSWORD': 'mungai',
        'TEST': {'CHARSET': 'UTF8'}
    }
}
import os
DJMAIL_REAL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = bool(os.environ.get("EMAIL_USE_TLS"))

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os
from celery.schedules import crontab
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, ActiveDirectoryGroupType
import logging

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)u1cm3&rk%j$5#%^n4@on@7rg-z8hjoa$k$_ln8q3)*j!_1r@#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



# Application definition
INSTALLED_APPS = [
    'daphne',
    'jazzmin',
    'api',
    'django_celery_results',
    'django_celery_beat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grants_management',
    'subgrantees',
    'financials',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'authentication',
    # 'django.contrib.messages',
    'notifications',
    'django_auth_ldap',
    'chats',
]
# CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_BROKER_URL = "redis://default:WcElpfpUKvjmBCpMCEXoBFEZkNuZdNCT@viaduct.proxy.rlwy.net:21260"
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = "Africa/Kampala"

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

ASGI_APPLICATION = 'BaylorGrants.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis: // default: WcElpfpUKvjmBCpMCEXoBFEZkNuZdNCT@viaduct.proxy.rlwy.net: 21260')],
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'BaylorGrants.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BaylorGrants.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        },
    }
}

SITE_URL = 'http://localhost:8000'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Serve static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'authentication.backend.CustomAuthenticationBackend',
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    
]

AUTH_USER_MODEL = 'authentication.CustomUser'


logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# LDAP Configuration
AUTH_LDAP_SERVER_URI = "ldap://dc01:389"

#LDAP Bind DN and Password
AUTH_LDAP_BIND_DN = "Baylor\\forms"
AUTH_LDAP_BIND_PASSWORD = "GeroWhat12345!"

#LDAP Base DN
AUTH_LDAP_BASE_DN = "dc=baylor,dc=local"

#LDAP User and Group search
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    AUTH_LDAP_BASE_DN,
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)"
)

#LDAP Group settings
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    AUTH_LDAP_BASE_DN,
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)"
)
AUTH_LDAP_GROUP_TYPE =ActiveDirectoryGroupType()

#LDAP attribute mappings
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

#Use LDAP group membership to determine permissions
AUTH_LDAP_FIND_GROUP_PERMS = True

#Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

#Keep users' LDAP passwords up-to-date
AUTH_LDAP_ALWAYS_UPDATE_USER = True
LDAP_DEBUG = True

# JWT Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=5),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'eazedairy@gmail.com'
EMAIL_HOST_PASSWORD = 'dngh jjwa fjux evkv'
DEFAULT_FROM_EMAIL = 'eazedairy@gmail.com'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development

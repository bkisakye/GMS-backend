from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os
from celery.schedules import crontab
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, ActiveDirectoryGroupType
import logging
# from authentication.backend import IntegratedAuthenticationBackend

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
    'reminders',
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
    'authentication.backend.IntegratedAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',

]

AUTH_USER_MODEL = 'authentication.CustomUser'


logger = logging.getLogger('django_auth_ldap')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# LDAP Configuration
AUTH_LDAP_SERVER_URI = "ldap://10.1.0.4:389"
# The DN for the service account used for binding
AUTH_LDAP_BIND_DN = "Baylor\\forms"
AUTH_LDAP_BIND_PASSWORD = "GeroWhat12345!"  # Ensure this is kept secure
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "dc=baylor,dc=local",  # Base DN for user searches
    ldap.SCOPE_SUBTREE,  # Search within the subtree
    "(sAMAccountName=%(user)s)"  # Filter to search by sAMAccountName
)

# Map LDAP attributes to user model fields
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "organisation_name": "sAMAccountName",
    "username": "sAMAccountName"  # Use 'username' if your user model expects this
    
}

# Group configuration
# Adjust this if you have a different group type
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
AUTH_LDAP_MIRROR_GROUPS = True  # Mirror LDAP groups to Django groups

# Make sure your group search base DN is correct; it seems you have a typo in "0u=groups"
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "dc=baylor,dc=local",  # Correct the typo here to 'ou=groups'
    ldap.SCOPE_SUBTREE,
    # Adjust if you are using a different object class
    "(objectClass=group)"
)

# Settings for user updates and bind behavior
# Update user info in Django from LDAP on login
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_BIND_AS_USER = True  # Bind as the user during authentication

# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_active": "CN=AllUsers,OU=Groups,DC=baylor,DC=local",
#     "is_staff": "CN=AllUsers,OU=Groups,DC=baylor,DC=local",
#     "is_approved": "CN=ActiveUsers, OU=Groups, DC=baylor, DC=local"
# }


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

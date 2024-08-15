"""
Django settings for LoongArch-ServerManager project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import sys
import logging
import dj_database_url
from pathlib import Path
from util.logger import Log
from .logger import InterceptHandler

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# sys.path.insert(0,os.path.join(BASE_DIR,'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h$p@2x!f5$2n8-f0d4xp#t1=d0_uhn2ld0sg2h3g^t2otbltz&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'daphne',  # WebSocket
    'channels',  # CHANNEL_LAYER
    'django_eventstream',  # SSE
    'apps.command_tool',  # 命令工具
    'apps.setting',  # 配置与设置
    'apps.auth',  # 认证
    'apps.user_manager',  # 用户管理器
    'apps.permission_manager',  # 权限管理器
    'apps.node_manager',  # 节点管理器
    "apps.group.manager",  # 集群管理器
    'apps.dashboard',  # 仪表盘
    'apps.audit',  # 审计
    'apps.message',  # 消息
    'apps.patrol',  # 巡检
    "apps.task",  # 任务管理
    "apps.web_status",  # 网站监控
    "apps.group.group_task",  # 集群任务
    "apps.group.commandExecution",  # 集群执行
    "apps.group.file_send",  # 集群文件分发
    'django.contrib.contenttypes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.AuthMiddleware.AuthMiddleware',
    # 'middleware.PermissionsMiddleware.PermissionsMiddleware',
    'middleware.APICallCounterMiddleware.APICallCounterMiddleware',
]

ROOT_URLCONF = 'LoongArch-ServerManager.urls'

WSGI_APPLICATION = 'LoongArch-ServerManager.wsgi.application'
ASGI_APPLICATION = 'LoongArch-ServerManager.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / './db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

# 存储带时区的时间
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR, 'static/assets')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.getenv('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv('REDIS_URL', "redis://localhost:6379"),
    }
}
# SECURE_CONTENT_TYPE_NOSNIFF = False

# 清空默认的Django日志配置
LOGGING_CONFIG = None

# 配置Django使用Loguru的日志处理器
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO if DEBUG else logging.WARNING)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,  # 禁用所有存在的日志记录器
    'handlers': {
        'loguru': {
            'class': 'LoongArch-ServerManager.logger.InterceptHandler',  # 将此路径替换为你定义的InterceptHandler的路径
        },
    },
    'root': {
        'handlers': ['loguru'],
        'level': "INFO",  # 仅输出INFO及以上级别的日志
    },
    'loggers': {
        'django': {
            'handlers': ['loguru'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['loguru'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['loguru'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

# 禁用所有默认的日志记录器
for logger_name in logging.root.manager.loggerDict.keys():
    logging.getLogger(logger_name).disabled = True

import os


SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'testapp',
    'flock',
]

MEDIA_ROOT = '/media/'
STATIC_URL = '/static/'
BASEDIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASEDIR, 'media/')
STATIC_ROOT = os.path.join(BASEDIR, 'static/')
SECRET_KEY = 'supersikret'
LOGIN_REDIRECT_URL = '/?login=1'

ROOT_URLCONF = 'testapp.urls'
LANGUAGES = (('en', 'English'), ('de', 'German'))
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_ROOT,"..", "mooch", "templates")],
        'APP_DIRS': True,
        "OPTIONS": {
            "context_processors": [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    }
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

STRIPE_PUBLISHABLE_KEY = 'nothing'
STRIPE_SECRET_KEY = 'nothing'
POSTFINANCE_PSPID = 'nothing'
POSTFINANCE_LIVE = False
POSTFINANCE_SHA1_IN = 'nothing'
POSTFINANCE_SHA1_OUT = 'nothing'

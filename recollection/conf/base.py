import os.path
import posixpath
import recollection
import pinax
from imp import find_module
from recollection.migrations import SOUTH_MIGRATION_MODULES

PINAX_ROOT=os.path.abspath(os.path.dirname(pinax.__file__))

RECOLLECTION_VERSION = recollection.__version__
RECOLLECTION_ROOT=os.path.abspath(os.path.dirname(recollection.__file__))

MEDIA_ROOT = os.path.join(RECOLLECTION_ROOT, "site_media", "media")
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(RECOLLECTION_ROOT, "site_media", 'static')
STATIC_URL = '/static/'

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

CMS_MEDIA_ROOT = os.path.join(STATIC_ROOT, 'cms/')
CMS_MEDIA_URL = os.path.join(STATIC_URL, 'cms/')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'changeme'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openid.consumer.SessionConsumer',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'recollection.utils.middleware.CMSToolbarPatchMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.media.PlaceholderMediaMiddleware',
)


ROOT_URLCONF = 'recollection.urls'


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "pinax.core.context_processors.pinax_settings",
    "recollection.utils.context_processors.recollection_settings",
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "account.context_processors.openid",
    "account.context_processors.account",
    #"messages.context_processors.inbox",
    "recollection.apps.connections.context_processors.invitations",
    "recollection.utils.context_processors.combined_inbox_count",
    "cms.context_processors.media",
)

COMBINED_INBOX_COUNT_SOURCES = (
    #"messages.context_processors.inbox",
    "recollection.apps.connections.context_processors.invitations",
    "notification.context_processors.notification",
)


INSTALLED_APPS = (
    'django.contrib.staticfiles',
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.admin',
    'pinax.templatetags',


    # external
    'notification', # must be first
    'django_openid',
    'emailconfirmation',
    'django_extensions',
    'robots',
    'friends',
    'mailer',
    'announcements',
    'pagination',
    'gravatar',
    'timezones',
    'ajax_validation',
    'avatar',
    'uni_form',
    'django_sorting',

    'pinax.apps.account',
    'recollection.apps.profiles',

    'compressor',
    'south',
    'piston',

    # CMS stuff
    'cms',
    'mptt',
    'menus',
    'publisher',
    'reversion',
    'cms.plugins.text',
    'cms.plugins.picture',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.snippet',

    # Freemix specific
    'freemix.utils',
    'freemix.transform',
    'freemix.dataprofile',
    'freemix.freemixprofile',
    'freemix.canvas',
    'freemix_mixer',
    'freemix.augment',
    'recollection.apps.notices',
    'recollection.apps.site_theme',
    'recollection.apps.collection_catalog',
    'recollection.apps.support',
    'recollection.utils',

    'recollection.apps.connections',
    'recollection.conf.recollection_defaults',
    #'recollection.datasources.cdm',
    #'recollection.datasources.oai',
    'django_redmine',

    'freemix.legacy.view_theme'

    )


STATICFILES_DIRS = (
    ('', os.path.join(RECOLLECTION_ROOT, 'static')),
    ('', os.path.join(PINAX_ROOT, 'media', 'default')),
    ('', os.path.join(os.path.abspath(os.path.dirname(__import__("uni_form").__file__)), 'media')),
    ('', os.path.join(os.path.abspath(os.path.dirname(__import__("ajax_validation").__file__)), 'media')),
    ('', os.path.join(os.path.abspath(os.path.dirname(__import__("pinax.apps.account").__file__)), 'media')),
    ('', os.path.join(os.path.abspath(os.path.dirname(__import__("django_extensions").__file__)), 'media')),
    ('', os.path.join(os.path.abspath(find_module('cms')[1]), 'media')),
)

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}
AUTH_PROFILE_MODULE = 'profiles.Profile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

THEME_DIR_URL = "themes/chili"
THEME_FRAGMENT_URL = "%s/chili.css"%THEME_DIR_URL
THEME_URL = '%s%s'%(STATIC_URL,THEME_FRAGMENT_URL)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(recollection.__file__), "templates"),
    os.path.join(os.path.dirname(pinax.__file__), "templates", "default"),
)

# Set to describe the site, properties and the names

SITE_NAME = "Recollection"
SITE_NAME_STATUS = "BETA"
CONTACT_EMAIL = "ndiippaccess@loc.gov"
DEFAULT_FROM_EMAIL = "webmaster@zepheira.com"
FEEDBACKLINK = "mailto:recollection@lists.zepheira.com"

LOGIN_URL = "/account/login"
LOGIN_REDIRECT_URLNAME = "user_home"

ANONYMOUS_USERNAME='guest'

ACCOUNT_OPEN_SIGNUP=False

ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False

FIXTURE_DIRS=(
    os.path.join(os.path.dirname(recollection.__file__), "fixtures"),
)

LOCALE_PATHS=(
    os.path.join(os.path.dirname(recollection.__file__), "locale"),
)

# Javascript and CSS compression
COMPRESS = False

# storage engine to be used during compression
COMPRESS_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# django-cms
CMS_TEMPLATES = (
    ('template.html', 'Front Page Template'),
    ('about/template.html', 'About Page Template'),
)

import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
)

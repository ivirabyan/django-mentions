import sys
from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    ROOT_URLCONF='mentions.urls',
    INSTALLED_APPS=('mentions',)
)

from django.test.simple import DjangoTestSuiteRunner


test_runner = DjangoTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(['mentions', ])

if failures:
    sys.exit(failures)

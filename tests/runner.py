import logging

from django.conf import settings

from django.test.runner import DiscoverRunner


class ScoringRunner(DiscoverRunner):
    def setup_test_environment(self):
        # No logging thanks
        logging.disable(logging.CRITICAL)
        super(ScoringRunner, self).setup_test_environment()
        # Use a faster password hasher
        settings.PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

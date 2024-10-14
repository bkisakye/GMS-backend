# File: your_app/management/commands/test_ldap.py

from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.conf import settings
import ldap


class Command(BaseCommand):
    help = 'Test LDAP connection and authentication'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        # Test LDAP connection
        try:
            conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN,
                               settings.AUTH_LDAP_BIND_PASSWORD)
            self.stdout.write(self.style.SUCCESS(
                'Successfully connected to LDAP server'))
        except ldap.LDAPError as e:
            self.stdout.write(self.style.ERROR(
                f'LDAP connection failed: {str(e)}'))
            return

        # Test user authentication
        user = authenticate(username=username, password=password)
        if user is not None:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully authenticated user: {user.username}'))
        else:
            self.stdout.write(self.style.ERROR('Authentication failed'))

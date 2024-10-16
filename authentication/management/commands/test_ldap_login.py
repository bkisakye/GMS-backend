from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate


class Command(BaseCommand):
    help = 'Test LDAP login'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='LDAP username')
        parser.add_argument('password', type=str, help='LDAP password')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            self.stdout.write(self.style.SUCCESS(
                'Successfully authenticated user: %s' % user.username))
        else:
            self.stdout.write(self.style.ERROR('Failed to authenticate user.'))

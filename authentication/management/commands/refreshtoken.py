from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

UserModel = get_user_model()


class Command(BaseCommand):
    help = 'Get API token for a given user. and if user not have token generate one'

    @staticmethod
    def create_user_token(username, reset_token):
        user = UserModel._default_manager.get_by_natural_key(username)

        if reset_token or not user.token:
            user.token = user.generate_token()
        return user.token

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

        parser.add_argument(
            '-r',
            '--reset',
            action='store_true',
            dest='reset_token',
            default=False,
            help='Reset existing User token and create a new one',
        )

    def handle(self, *args, **options):
        username = options['username']
        reset_token = options['reset_token']

        try:
            token = self.create_user_token(username, reset_token)
        except UserModel.DoesNotExist:
            raise CommandError(f'Cannot create a token: user {username} does not exist')

        self.stdout.write(f'Generated 🥳: {token}')

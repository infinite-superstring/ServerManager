from django.core.management import BaseCommand
from apps.user_manager.models import User
from util.logger import Log
from util.passwordUtils import GeneratePassword, encrypt_password


class Command(BaseCommand):
    help = 'Reset admin user'

    def handle(self, *args, **options):
        user = User.objects.get(id=1)
        defaultPassword = GeneratePassword(16)
        hashed_password, salt = encrypt_password(defaultPassword)
        user.userName = "admin"
        user.password = hashed_password
        user.passwordSalt = salt
        user.save()
        Log.info('Admin user reset successfully, Password:'+defaultPassword)
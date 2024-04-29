from django.core.management import BaseCommand
from user_manager.models import User
from util.logger import Log
from util.passwordUtils import GeneratePassword, PasswordToMd5

class Command(BaseCommand):
    help = 'Reset admin user'

    def handle(self, *args, **options):
        user = User.objects.get(id=1)
        defaultPassword = GeneratePassword(16)
        user.userName = "admin"
        user.password = PasswordToMd5(defaultPassword)
        user.save()
        Log.info('Admin user reset successfully, Password:'+defaultPassword)
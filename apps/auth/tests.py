from django.test import TestCase
from apps.auth.utils.authCodeUtils import *

# Create your tests here.

class AuthTests(TestCase):
    user: User = None
    def setUp(self):
        from apps.user_manager.models import User
        self.user = User.objects.create(
            userName='testuser',
            email='fsjasd123456@gmail.com',
            passwordSalt="123456"
        )

    def test_send_auth_code(self):
        """测试验证码发送"""
        send_auth_code(self.user)
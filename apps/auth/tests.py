from django.test import TestCase
from apps.auth.utils.authCodeUtils import *
import qrcode
import pyotp

# Create your tests here.

class AuthTests(TestCase):
    user: User = None
    def setUp(self):
        pass
        # from apps.user_manager.models import User
        # self.user = User.objects.create(
        #     userName='testuser',
        #     email='fsjasd123456@gmail.com',
        #     passwordSalt="123456"
        # )

    # def test_send_auth_code(self):
    #     """测试验证码发送"""
    #     send_auth_code(self.user)

    def test_generate_otp_code(self):
        token = pyotp.random_hex()
        qr_code = pyotp.hotp.HOTP(token).provisioning_uri(name="app@app.com", issuer_name="Test App", initial_count=0)
        img = qrcode.make(qr_code)
        img.save("qr_code.png")

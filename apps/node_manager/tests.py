import secrets

from django.test import TestCase

from util.passwordUtils import PasswordToMd5


# Create your tests here.

class NodeManagerTestCase(TestCase):
    def test_GenerateToken(self):
        token = secrets.token_hex(64)
        print(str(token))
        print(len(token))
        md5 = PasswordToMd5(str(token))
        print(md5)
        print(len(md5))
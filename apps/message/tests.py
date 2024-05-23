import datetime

from django.test import TestCase

from apps.message.api.message import get_message_list
from apps.message.models import Message, MessageBody
from apps.message.utils.sendEmailUtil import send
from util.passwordUtils import encrypt_password


# Create your tests here.

class MessageTest(TestCase):

    def test(self):
        send(MessageBody(title="这是一封测试邮件", content="我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容我是内容"))

    def test1(self):
        password, salt = encrypt_password("123456")
        print(password)
        print(salt)




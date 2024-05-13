import datetime

from django.test import TestCase

from apps.message.api.message import get_message_list
from apps.message.models import Message


# Create your tests here.

class MessageTest(TestCase):

    def test(self):
        Message.objects.create(title="测试", content="测试" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),created_at=datetime.datetime.now(),updated_at=datetime.datetime.now())
        result = get_message_list({})
        print(result.getvalue())



"""        User.objects.create(
            userName='test',
            realName='test',
            email='1101658312@qq.com',
            password='123456',
            passwordSalt='1234567',
            disable=False,
            )
        User.objects.create(
            userName='test1',
            realName='test1',
            email='3072864687@qq.com',
            password='123456',
            passwordSalt='123456',
            disable=False,
            )
        send_email(MessageBody("测试", "测试" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))"""

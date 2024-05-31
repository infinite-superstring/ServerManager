from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.test import TestCase

from apps.message.api.message import get_message_list
from apps.message.models import Message, MessageBody
from apps.message.utils.messageUtil import send
from apps.user_manager.models import User
from util.passwordUtils import encrypt_password
from apps.message.webSockets.message_client import MessageClient


# Create your tests here.

class MessageTest(TestCase):

    def test(self):
        pass

    def test1(self):
        password, salt = encrypt_password("123456")
        print(password)
        print(salt)

    def test2(self):
        pass

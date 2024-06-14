from datetime import datetime, time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.test import TestCase

from apps.message.api.message import get_message_list
from apps.message.models import Message, MessageBody
from apps.message.utils.messageUtil import send
from apps.node_manager.models import Node_Group, Node_MessageRecipientRule
from apps.node_manager.utils.groupUtil import create_message_recipient_rule, create_message_recipient_rules
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
        for i in range(10):
            password, salt = encrypt_password("123456")
            User.objects.create(
                userName=str(i + 1) + "test",
                realName=str(i) + "test",
                email=str(i) + "test@test.com",
                password=password,
                passwordSalt=salt)
        # Node_MessageRecipientRule.objects.create(
        #     monday=True,
        #     tuesday=True,
        #     wednesday=True,
        #     thursday=True,
        #     friday=True,
        #     saturday=True,
        #     sunday=True,
        #     start_time="08:00",
        #     end_time="18:00",
        #     recipients=User.objects.filter(id__in=[1, 2, 3, 4, 5]))
        # ng = Node_Group.objects.create(name="test", description="test", leader=User.objects.get(id=1))
        # ng.time_slot_recipient.add(Node_MessageRecipientRule.objects.get(id=1))
        # ng = create_message_recipient_rule(
        #     week=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', ],
        #     start_time="08:00",
        #     end_time="18:00",
        #     users=User.objects.filter(id__in=[1, 2, 3, 4, 5])
        # )
        ng = Node_Group.objects.create(name="test", description="test", leader=User.objects.get(id=6))
        rules = create_message_recipient_rules(
            data=[
                {
                    "week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                    "start_time": "3:00",
                    "end_time": "3:13",
                    "users": [1, 2, 3, 4, 5]
                },
            ])
        ng.time_slot_recipient.add(*rules)
        now = datetime.now()
        current_time = time(now.hour, now.minute)
        a = Node_MessageRecipientRule.objects.filter(start_time__lte=current_time, end_time__gte=current_time)
        send(MessageBody(title="test", content="test", name="test", node_groups=Node_Group.objects.filter()))

    def test3(self):

        send(MessageBody(title="test", content="test", name="test", recipient=User.objects.get(id=1)))

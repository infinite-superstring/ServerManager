from datetime import datetime, time

from django.test import TestCase

from apps.message.models import MessageBody
from apps.message.utils.messageUtil import send
from apps.group.manager.models import Node_Group
from apps.node_manager.utils.groupUtil import create_node_group_user_permission_rules
from apps.user_manager.models import User
from util.passwordUtils import encrypt_password


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
        #     user_list=User.objects.filter(id__in=[1, 2, 3, 4, 5]))
        # ng = Node_Group.objects.create(name="test", description="test", leader=User.objects.get(id=1))
        # ng.user_permission.add(Node_MessageRecipientRule.objects.get(id=1))
        # ng = create_message_recipient_rule(
        #     week=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', ],
        #     start_time="08:00",
        #     end_time="18:00",
        #     users=User.objects.filter(id__in=[1, 2, 3, 4, 5])
        # )
        ng = Node_Group.objects.create(name="test", description="test", leader=User.objects.get(id=6))
        rules = create_node_group_user_permission_rules(data=[
            {
                "week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                "start_time": "3:00",
                "end_time": "3:13",
                "users": [1, 2, 3, 4, 5]
            },
        ])
        ng.user_permission.add(*rules)
        now = datetime.now()
        current_time = time(now.hour, now.minute)
        # a = Node_MessageRecipientRule.objects.filter(start_time__lte=current_time, end_time__gte=current_time)
        send(MessageBody(title="test", content="test", name="test", node_groups=Node_Group.objects.filter()))

    def test3(self):
        send(MessageBody(title="test", content="test", name="test", recipient=User.objects.get(id=1)))

    def test4(self):
        l = [1, 2, 3, 4, 5, 6, 7]
        handelList(l)
        print(l)

    def test5(self):
        print(not None)


def handelList(l):
    print(l)
    l.pop()

from django.test import TestCase

from apps.task.models import Task
from apps.task.utils.taskUtil import get_today_start_time, get_today_end_time, createAttendance, \
    byUserIDGetAttendanceState
from apps.user_manager.models import User


# Create your tests here.

class taskTest(TestCase):

    def test(self):
        User.objects.create(
            userName="test",
            realName="test",
            email="test",
            password="test",
            passwordSalt="test",
            avatar="test",
            disable=False
        )
        createAttendance(user_id=1)
        task = byUserIDGetAttendanceState(user_id=1)
        tasks = Task.objects.get(id=1)
        print(task)
        print(tasks)

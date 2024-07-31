import datetime

from django.test import TestCase

from apps.group.node_task.utils import group_task_util


# Create your tests here.
class Test(TestCase):
    def test(self):
        # 获取当前本地时间
        local_now = datetime.datetime.now()

        # 获取当前UTC时间
        utc_now = datetime.datetime.utcnow()

        # 计算本地时间和UTC时间的偏移量
        offset = local_now - utc_now

        # 输出偏移量
        print(offset.total_seconds())

    def test1(self):
        test_data = open('test.txt', 'w+', encoding='utf-8')
        print(type(test_data).__name__)
        test_data.write('一行\n')

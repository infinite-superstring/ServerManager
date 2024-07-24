import uuid
from django.db import models

from apps.node_manager.models import Node_Group, Node
from apps.task.models import Task
from apps.user_manager.models import User


# Create your models here.

class file_distribution_task(models.Model):
    uuid = models.UUIDField("节点UUID", primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Node_Group, on_delete=models.CASCADE)  # 分发集群
    files = models.ManyToManyField("file_list", related_name='files')
    receive_directory = models.CharField("文件接收目录", max_length=1024, null=True)
    creation_time = models.DateTimeField("分发任务创建时间", auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    progress = models.ManyToManyField("Progress", related_name='progress')

    class Meta:
        db_table = 'file_distribution_task'
        db_table_comment = '文件分发任务'

    class Progress(models.Model):
        PROGRESS_CHOICES = [
            ('Success', 'Success'),
            ('Failure', 'Failure'),
            ('Offline', 'Offline'),
        ]
        task = models.ForeignKey(Task, on_delete=models.CASCADE)
        node = models.ForeignKey(Node, on_delete=models.CASCADE)
        status = models.CharField("节点分发状态", max_length=10, choices=PROGRESS_CHOICES)

        class Meta:
            db_table = 'file_distribution:progress'
            db_table_comment = "文件分发任务 - 进度"


class file_list(models.Model):
    file_name = models.CharField("文件名", max_length=255, unique=True)
    file_hash = models.CharField("文件哈希", max_length=255, unique=True)
    upload_time = models.DateTimeField("文件上传时间", auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'file_distribution:file_list'
        db_table_comment = "文件分发任务 - 文件列表"

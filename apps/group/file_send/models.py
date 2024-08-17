import uuid
from django.db import models

from apps.node_manager.models import Node
from apps.group.manager.models import Node_Group
from apps.task.models import Task
from apps.user_manager.models import User


# Create your models here.

class File_DistributionTask(models.Model):
    uuid = models.UUIDField("节点UUID", primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Node_Group, on_delete=models.CASCADE)  # 分发集群
    files = models.ManyToManyField("FileDistribution_FileList", related_name='files')
    receive_directory = models.CharField("文件接收目录", max_length=1024, null=True)
    creation_time = models.DateTimeField("分发任务创建时间", auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    progress = models.ManyToManyField("Progress", related_name='progress')

    class Meta:
        db_table = 'file_distribution_task'
        db_table_comment = '文件分发任务'

    class Progress(models.Model):
        PROGRESS_CHOICES = [
            ('Activity', 'Activity'),
            ('Success', 'Success'),
            ('Failure', 'Failure'),
            ('Offline', 'Offline'),
        ]
        # 节点实例
        node = models.ForeignKey(Node, on_delete=models.CASCADE)
        # 总体状态
        status = models.CharField("节点分发状态", max_length=15, choices=PROGRESS_CHOICES)
        # 成功的文件
        success_files = models.ManyToManyField("FileDistribution_FileList", related_name='success_files')
        # 失败的文件
        failure_files = models.ManyToManyField("FileDistribution_FileList", related_name='failure_files')

        class Meta:
            db_table = 'file_distribution:progress'
            db_table_comment = "文件分发任务 - 进度"


class FileDistribution_FileList(models.Model):
    file_name = models.ManyToManyField('FileName')
    file_hash = models.CharField("文件哈希", max_length=255, unique=True)
    upload_time = models.DateTimeField("文件上传时间", auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'file_distribution:file_list'
        db_table_comment = "文件分发任务 - 文件列表"

    class FileName(models.Model):
        task = models.ForeignKey(File_DistributionTask, null=False, on_delete=models.CASCADE)
        name = models.CharField(max_length=255)

        class Meta:
            db_table = 'file_distribution:file_name'
            db_table_comment = '文件分发任务 - 文件名'

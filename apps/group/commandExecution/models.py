import uuid
from django.db import models

from apps.group.manager.models import Node_Group
from apps.user_manager.models import User


# Create your models here.

# 集群执行
class Cluster_Execute(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 组
    group = models.ForeignKey(Node_Group, on_delete=models.CASCADE)
    # 发起者
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 执行目录
    base_path = models.CharField(max_length=512, null=True)
    # Shell命令
    shell = models.CharField(max_length=8192, null=False)
    # 发起时间
    timestamp = models.DateTimeField(auto_now_add=True)


# 集群执行返回
class Cluster_ExecuteResult(models.Model):
    models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Cluster_Execute, on_delete=models.CASCADE)
    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

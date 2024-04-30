from django.db import models
from django.utils import timezone


# Create your models here.


class Node(models.Model):
    """节点列表"""
    # 节点ID
    id = models.AutoField(primary_key=True)
    # 节点名称
    name = models.CharField(max_length=100, unique=True, null=False)
    # 节点Token
    token = models.CharField(max_length=256, unique=True, null=False)
    # 节点系统信息
    info = models.ForeignKey('Node_BaseInfo', on_delete=models.DO_NOTHING, null=False)
    # 节点介绍
    description = models.CharField(max_length=100, null=True)
    # 节点标签列表
    tags = models.ManyToManyField('Node_Tag', related_name='tags')
    # 节点分组
    group = models.ForeignKey('Node_Group', on_delete=models.DO_NOTHING, null=True)


class Node_BaseInfo(models.Model):
    """节点信息"""
    id = models.AutoField(primary_key=True)
    # 操作系统
    system = models.CharField(max_length=100, unique=False, null=True)
    # 操作系统版本
    system_release = models.CharField(max_length=100, unique=False, null=True)
    # 操作系统编译版本
    system_build_version = models.CharField(max_length=100, unique=False, null=True)
    # 主机名
    hostname = models.CharField(max_length=100, unique=False, null=True)
    # 启动时间
    boot_time = models.CharField(max_length=100, unique=False, null=True)
    # 在线状态
    online = models.BooleanField(default=False, null=False)


class Node_Tag(models.Model):
    """节点标签"""
    id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=100, unique=True, null=True)


class Node_Group(models.Model):
    """节点组"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False)


class Node_UsageData(models.Model):
    """节点使用率数据"""
    # 节点
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    # 更新时间
    timestamp = models.DateTimeField(auto_now_add=True)
    # CPU使用率
    cpu_usage = models.FloatField()
    # 总内存
    total_memory = models.BigIntegerField()
    # 可用内存
    available_memory = models.BigIntegerField()
    # 已用内存
    used_memory = models.BigIntegerField()
    # 磁盘IO - 写字节数
    disk_read_bytes = models.BigIntegerField()
    # 磁盘IO - 读字节数
    disk_write_bytes = models.BigIntegerField()
    # 网络 - 发送字节数
    network_bytes_sent = models.BigIntegerField()
    # 网络 - 接收字节数
    network_bytes_recv = models.BigIntegerField()


# 动态创建按月份分表的模型类
def create_node_data_table():
    current_month = timezone.now().strftime('%Y%m')
    table_name = f"Node_UsageData_{current_month}"

    class Meta:
        db_table = table_name
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    attrs = {
        '__module__': __name__,
        'Meta': Meta,
    }

    return type('NodeDataMonthly', (Node_UsageData,), attrs)

import uuid
from django.db import models
from django.utils import timezone


# Create your models here.


class Node(models.Model):
    """节点列表"""
    uuid = models.UUIDField("节点UUID", primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("节点名称", max_length=100, unique=True, null=False)
    token_hash = models.CharField("节点Token Hash值", max_length=256, unique=True, null=False)
    token_salt = models.CharField("节点Token盐值", max_length=256, unique=True, null=False)
    description = models.CharField("节点简介", max_length=100, null=True)
    # 节点标签列表
    tags = models.ManyToManyField('Node_Tag', related_name='tags')
    # 节点分组
    group = models.ForeignKey('Node_Group', on_delete=models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'node_list'
        db_table_comment = '节点列表'


class Node_BaseInfo(models.Model):
    """节点信息"""
    node = models.OneToOneField(Node, on_delete=models.CASCADE, null=False)
    node_version = models.CharField("节点版本", max_length=256, null=True)
    system = models.CharField("节点操作系统类型", max_length=100, unique=False, null=True)
    system_release = models.CharField("节点操作系统版本", max_length=100, unique=False, null=True)
    system_build_version = models.CharField("节点操作系统编译版本", max_length=100, unique=False, null=True)
    memory_total = models.BigIntegerField("节点内存总量", null=True)
    swap_total = models.BigIntegerField("节点交换空间总量", null=True)
    hostname = models.CharField("节点主机名", max_length=100, unique=False, null=True)
    boot_time = models.DateTimeField("节点系统运行时间", null=True),
    disk_list = models.ManyToManyField("Node_DiskPartition", related_name='disk_list')
    online = models.BooleanField("节点在线状态", default=False, null=False)

    class Meta:
        db_table = 'node_base_info'
        db_table_comment = '节点基础信息'


class Node_Tag(models.Model):
    """节点标签"""
    id = models.AutoField("标签ID", primary_key=True)
    tag_name = models.CharField("标签名", max_length=100, unique=True, null=True)

    class Meta:
        db_table = 'node_tags'
        db_table_comment = '节点标签列表'


class Node_Group(models.Model):
    """节点组"""
    id = models.AutoField("组ID", primary_key=True)
    name = models.CharField("组名", max_length=100, unique=True, null=False)

    class Meta:
        db_table = 'node_groups'
        db_table_comment = '节点组列表'


class Node_UsageData(models.Model):
    """节点使用率数据"""
    # 节点
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    # 更新时间
    timestamp = models.DateTimeField("更新时间", auto_now_add=True)
    # CPU
    cpu = models.ManyToManyField('Cpu_Usage', related_name='cpu_cores_usage_mapping')
    # 内存
    memory_used = models.BigIntegerField("内存使用量", null=False)
    # 交换空间
    swap_used = models.BigIntegerField("交换空间使用量", null=False)
    # 磁盘io
    disk_io_read_bytes = models.BigIntegerField("磁盘IO-读字节数(s/bytes)", null=False)
    disk_io_write_bytes = models.BigIntegerField("磁盘IO-写字节数(s/bytes)", null=False)

    class Meta:
        db_table = 'node_usage_data'
        db_table_comment = '节点使用率数据'

    class Cpu_Usage(models.Model):
        """CPU核心使用率"""
        core_index = models.IntegerField("核心")
        usage = models.FloatField("使用率")

        class Meta:
            db_table = 'cpu_core_usage'
            db_table_comment = 'CPU核心使用率数据'


class Node_DiskPartition(models.Model):
    """磁盘分区信息"""
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    device = models.CharField("设备", max_length=100, null=False)
    mount_point = models.CharField("挂载点", max_length=100, null=True)
    fs_type = models.CharField("文件系统", max_length=100, null=True)
    total = models.BigIntegerField("容量", null=True)
    used = models.BigIntegerField("已用空间", null=True)

    class Meta:
        db_table = 'node_disk_partition_list'
        db_table_comment = '分区列表'
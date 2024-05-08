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


class Node_BaseInfo(models.Model):
    """节点信息"""
    node = models.OneToOneField(Node, on_delete=models.CASCADE, null=False)
    node_version = models.CharField("节点版本", max_length=256, null=True)
    system = models.CharField("节点操作系统类型", max_length=100, unique=False, null=True)
    system_release = models.CharField("节点操作系统版本", max_length=100, unique=False, null=True)
    system_build_version = models.CharField("节点操作系统编译版本", max_length=100, unique=False, null=True)
    hostname = models.CharField("节点主机名", max_length=100, unique=False, null=True)
    boot_time = models.DateTimeField("节点系统运行时间", null=True),
    disk_list = models.ManyToManyField("Node_Disk", related_name='disk_list')
    auth_ip = models.CharField("认证IP", max_length=100, unique=False, null=False)
    online = models.BooleanField("节点在线状态", default=False, null=False)


class Node_Tag(models.Model):
    """节点标签"""
    id = models.AutoField("标签ID", primary_key=True)
    tag_name = models.CharField("标签名", max_length=100, unique=True, null=True)


class Node_Group(models.Model):
    """节点组"""
    id = models.AutoField("组ID", primary_key=True)
    name = models.CharField("组名", max_length=100, unique=True, null=False)


class Node_UsageData(models.Model):
    """节点使用率数据"""
    # 节点
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    # 更新时间
    timestamp = models.DateTimeField(auto_now_add=True)
    # CPU使用率
    cpu_usage = models.ManyToManyField('Cpu_Usage', related_name='cpu_cores_usage_mapping')
    memory_usage = models.ForeignKey('Memory_Usage', on_delete=models.CASCADE, related_name='memory_usage_mapping')
    swap_usage = models.ForeignKey('Swap_Usage', on_delete=models.CASCADE, related_name='swap_usage_mapping')
    # # 网络 - 发送字节数
    # network_bytes_sent = models.BigIntegerField()
    # # 网络 - 接收字节数
    # network_bytes_recv = models.BigIntegerField()

    class Cpu_Usage(models.Model):
        """CPU核心使用率"""
        core_index = models.IntegerField()
        usage = models.FloatField()

    class Memory_Usage(models.Model):
        """内存使用率"""
        total = models.BigIntegerField()
        used = models.BigIntegerField()

    class Swap_Usage(models.Model):
        """交换空间使用率"""
        total = models.BigIntegerField()
        used = models.BigIntegerField()

    class Disk_IO_Usage(models.Model):
        """磁盘IO使用"""
        disk = models.ForeignKey("Node_Disk", on_delete=models.CASCADE, related_name='disk_usage_mapping')
        read_count = models.BigIntegerField("读计数器", null=False)
        write_count = models.BigIntegerField("写计数器", null=False)
        read_bytes = models.BigIntegerField("读字节数", null=False)
        write_bytes = models.BigIntegerField("写字节数", null=False)



class Node_Disk(models.Model):
    """磁盘信息"""
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    device = models.CharField("设备", max_length=100, null=False)
    mount_point = models.CharField("挂载点", max_length=100, null=True)
    fs_type = models.CharField("文件系统", max_length=100, null=True)
    total = models.BigIntegerField("容量", null=True)
    used = models.BigIntegerField("已用空间", null=True)



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

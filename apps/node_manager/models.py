import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
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
    architecture = models.CharField("处理器架构", max_length=50, null=True)
    core_count = models.IntegerField("处理器核心数", null=True)
    processor_count = models.IntegerField("处理器线程数", null=True)
    hostname = models.CharField("节点主机名", max_length=100, unique=False, null=True)
    boot_time = models.DateTimeField("节点系统运行时间", null=True)
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
    description = models.CharField("节点组简介", max_length=100, null=True)
    leader = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    time_slot_recipient = models.ManyToManyField(
        "Node_MessageRecipientRule",
        related_name='time_slot_recipient_mappings'
    )

    class Meta:
        db_table = 'node_groups'
        db_table_comment = '节点组列表'


class Node_MessageRecipientRule(models.Model):
    """消息接收人"""
    id = models.AutoField("ID", primary_key=True)
    monday = models.BooleanField("星期一", null=False)
    tuesday = models.BooleanField("星期二", null=False)
    wednesday = models.BooleanField("星期三", null=False)
    thursday = models.BooleanField("星期四", null=False)
    friday = models.BooleanField("星期五", null=False)
    saturday = models.BooleanField("星期六", null=False)
    sunday = models.BooleanField("星期日", null=False)
    start_time = models.TimeField("开始时间", null=False)
    end_time = models.TimeField("结束时间", null=False)
    recipients = models.ManyToManyField("user_manager.User", related_name='node_message_recipients_mapping')

    class Meta:
        db_table = 'node_message_recipient'
        db_table_comment = "节点消息接收人"


class Node_UsageData(models.Model):
    """节点使用率数据"""
    # 节点
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    # 更新时间
    timestamp = models.DateTimeField("更新时间", auto_now_add=True)
    # CPU
    cpu_core_usage = models.ManyToManyField('CpuCoreUsage', related_name='cpu_cores_usage_mapping')
    # Cpu总体使用率
    cpu_usage = models.BigIntegerField("Cpu总体使用率", null=False, default=0)
    # 内存
    memory_used = models.BigIntegerField("内存使用量", null=False)
    # 交换空间
    swap_used = models.BigIntegerField("交换空间使用量", null=False)
    # 磁盘io
    disk_io_read_bytes = models.BigIntegerField("磁盘IO-读字节数(s/bytes)", null=False)
    disk_io_write_bytes = models.BigIntegerField("磁盘IO-写字节数(s/bytes)", null=False)
    # 网络
    network_usage = models.ManyToManyField("NetworkUsage", related_name='network_usage_mapping')
    # 系统平均负载
    system_loadavg = models.OneToOneField("Loadavg", on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'node_usage_data'
        db_table_comment = '节点使用率数据'

    class CpuCoreUsage(models.Model):
        """CPU核心使用率"""
        core_index = models.IntegerField("核心")
        usage = models.FloatField("使用率")

        class Meta:
            db_table = 'cpu_core_usage'
            db_table_comment = 'CPU核心使用率数据'

    class Loadavg(models.Model):
        one_minute = models.FloatField("一分钟平均负载")
        five_minute = models.FloatField("5分钟平均负载")
        fifteen_minute = models.FloatField("15分钟平均负载")

        class Meta:
            db_table = 'loadavg'
            db_table_comment = '系统平均负载'

    class NetworkUsage(models.Model):
        port_name = models.CharField("网络端口名", max_length=100)
        bytes_sent = models.BigIntegerField("发送的字节数")
        bytes_recv = models.BigIntegerField("接收的字节数")

        class Meta:
            db_table = 'network_usage'
            db_table_comment = "网络接口负载"


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


# 节点事件
class Node_Event(models.Model):
    SEVERITY_CHOICES = [
        ('Info', 'Info'),
        ('Warning', 'Warning'),
        ('Error', 'Error'),
        ('Critical', 'Critical'),
    ]
    id = models.AutoField("事件ID", primary_key=True)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    type = models.CharField("事件类型", max_length=100)
    description = models.CharField("事件详细描述", max_length=200, null=True)
    level = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'node_events'
        db_table_comment = '节点事件'


# 节点告警设置
class Node_AlarmSetting(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    enable = models.BooleanField(default=False)
    delay_seconds = models.IntegerField("告警延迟时间(秒)", null=False, default=1)
    interval = models.IntegerField("告警间隔时间", null=False, default=60)
    general_rules = models.ManyToManyField('GeneralAlarmRule')
    disk_used_rules = models.ManyToManyField('DiskUsedAlarmRule')
    network_rule = models.ForeignKey('NetworkAlarmRule', on_delete=models.CASCADE)

    # 告警规则基类
    class Base_AlarmRule(models.Model):
        MODULE_CHOICES = [
            ('CPU', 'CPU'),  # 百分比
            ('Memory', 'Memory'),  # 百分比
            ('Disk', 'Disk'),  # 设备 百分比
            ('Network', 'Network'),  # 最大Bytes
        ]
        module = models.CharField(max_length=50, choices=MODULE_CHOICES)
        enable = models.BooleanField(default=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

    # 通用告警设置
    class GeneralAlarmRule(Base_AlarmRule):
        threshold = models.BigIntegerField("阈值")

    # 磁盘告警设置
    class DiskUsedAlarmRule(Base_AlarmRule):
        device = models.ForeignKey('Node_DiskPartition', on_delete=models.CASCADE)
        threshold = models.IntegerField("磁盘空间百分比")

    # 网络告警设置
    class NetworkAlarmRule(Base_AlarmRule):
        send_threshold = models.BigIntegerField("发送最大阈值(bytes/s)")
        receive_threshold = models.BigIntegerField("接收最大阈值(bytes/s)")

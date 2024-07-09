from django.db import models
import uuid


# Create your models here.

class GroupTask(models.Model):
    uuid = models.UUIDField("uuid", primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("任务名称", max_length=64, unique=True)
    node_group = models.ForeignKey(to="node_manager.Node_Group", on_delete=models.CASCADE, related_name='group_tasks')
    exec_type = models.CharField("执行类型", max_length=32)
    """
    指定时间 -> 'date-time'
    周期 -> 'cycle'
    间隔 -> 'interval'
    """
    interval = models.IntegerField("执行间隔", null=True)
    that_time = models.DateTimeField("指定时间", null=True)
    exec_count = models.IntegerField("执行次数", null=True)
    command = models.TextField("执行命令", max_length=8192)
    enable = models.BooleanField("启用", default=True)
    exec_path = models.CharField("执行路径", max_length=256, null=True)

    class Meta:
        db_table = "group_task"
        db_table_comment = "任务记录"


class GroupTask_Cycle(models.Model):
    group_task = models.ForeignKey(to="GroupTask", on_delete=models.CASCADE, related_name='group_task_cycles')
    time = models.TimeField("执行时间")
    sunday = models.BooleanField("周日", default=False, null=False)
    monday = models.BooleanField("周一", default=False, null=False)
    tuesday = models.BooleanField("周二", default=False, null=False)
    wednesday = models.BooleanField("周三", default=False, null=False)
    thursday = models.BooleanField("周四", default=False, null=False)
    friday = models.BooleanField("周五", default=False, null=False)
    saturday = models.BooleanField("周六", default=False, null=False)

    class Meta:
        db_table = "group_task_cycle"
        db_table_comment = "任务周期"


class Group_Task_Audit(models.Model):
    uuid = models.UUIDField("uuid", primary_key=True, default=uuid.uuid4, editable=False)
    group_task = models.ForeignKey(to="GroupTask", on_delete=models.CASCADE, related_name='group_task_audits')
    node = models.ForeignKey(to='node_manager.Node', on_delete=models.CASCADE, related_name='group_task_audits')
    status = models.CharField("状态", max_length=32)
    statr_time = models.DateTimeField("开始时间", auto_now_add=True)
    end_time = models.DateTimeField("结束时间", null=True)

    class Meta:
        db_table = "group_task_audit"
        db_table_comment = "任务审计"

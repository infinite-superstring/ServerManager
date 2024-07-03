from django.db import models


# Create your models here.

class GroupTask(models.Model):
    name = models.CharField("任务名称", max_length=64)
    node_group = models.ForeignKey(to="node_manager.Node_Group", on_delete=models.CASCADE, related_name='group_tasks')
    exec_type = models.CharField("执行类型", max_length=32)
    interval = models.IntegerField("执行间隔")
    cycle = models.ForeignKey(to="GroupTask_Cycle", on_delete=models.CASCADE, related_name='group_task_cycles')
    that_time = models.DateTimeField("指定时间")
    exec_count = models.IntegerField("执行次数")
    command = models.TextField("执行命令", max_length=8192)

    class Meta:
        db_table = "group_task"
        db_table_comment = "任务记录"


class GroupTask_Cycle(models.Model):
    group_task = models.ForeignKey(to="GroupTask", on_delete=models.CASCADE, related_name='group_task_cycles')
    time = models.TimeField("执行时间")
    sunday = models.BooleanField("周日")
    monday = models.BooleanField("周一")
    tuesday = models.BooleanField("周二")
    wednesday = models.BooleanField("周三")
    thursday = models.BooleanField("周四")
    friday = models.BooleanField("周五")
    saturday = models.BooleanField("周六")

    class Meta:
        db_table = "group_task_cycle"
        db_table_comment = "任务周期"

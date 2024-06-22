from django.db import models


# Create your models here.

class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    init_User = models.ForeignKey(to="user_manager.User", on_delete=models.CASCADE, related_name='initiated_tasks',default=None,null=True)
    target_user = models.ForeignKey(to="user_manager.User", on_delete=models.CASCADE, related_name='targeted_tasks',default=None,null=True)
    start_time = models.DateTimeField("任务开始时间", auto_now_add=True)
    need_end_time = models.DateTimeField("需要结束时间", null=True)
    end_time = models.DateTimeField("任务结束时间", null=True)
    status = models.IntegerField("任务状态")
    type = models.IntegerField("任务类型")
    description = models.CharField("任务描述", max_length=512)
    result = models.CharField("任务结果", max_length=4096)

    class Meta:
        db_table = "task"
        db_table_comment = "任务记录"

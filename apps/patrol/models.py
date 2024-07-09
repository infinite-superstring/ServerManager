from django.db import models


# Create your models here.

class Patrol(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    status = models.CharField("状态", max_length=256)
    content = models.CharField("内容", max_length=4096)
    title = models.CharField("title", max_length=256)
    time = models.DateTimeField("巡检时间", auto_now_add=True)

    class Meta:
        db_table = "patrol"
        db_table_comment = "巡检记录"

from django.db import models


# Create your models here.

# 设置
class Settings(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    Settings = models.CharField("设置项名", max_length=120, unique=True)
    value = models.CharField("值", max_length=4096)
    lastModifiedTime = models.DateTimeField("上次修改时间", null=True, auto_now=True)
    lastModifiedUser = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'setting'
        db_table_comment = "设置"

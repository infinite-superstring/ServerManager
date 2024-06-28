from django.db import models


# Create your models here.

class Web_Status(models.Model):
    """
    Web状态
    """
    id = models.AutoField(primary_key=True, unique=True)
    status = models.IntegerField("状态", default=404)
    online = models.BooleanField("是否在线", default=False)
    delay = models.IntegerField("延迟", default=0)
    title = models.CharField("标题", max_length=256)
    host = models.CharField("主机", max_length=256, unique=True)
    description = models.CharField("描述", max_length=256)

    class Meta:
        db_table = "web_status"
        verbose_name = 'Web状态'

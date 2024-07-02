from django.db import models


# Create your models here.

class Web_Site(models.Model):
    """
    Web状态
    """
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField("标题", max_length=256)
    host = models.CharField("主机", max_length=256, unique=True)
    description = models.CharField("描述", max_length=256)

    class Meta:
        db_table = "web_status"
        verbose_name = 'Web状态'


class Web_Site_Abnormal_Log(models.Model):
    """
    Web警告日志
    """
    web = models.ForeignKey('web_status.Web_Site', on_delete=models.CASCADE)
    status = models.IntegerField("状态码", default=500)
    error_type = models.CharField("错误类型", max_length=256)
    error_info = models.CharField("错误信息", max_length=256)
    start_time = models.DateTimeField("开始时间", null=True)
    end_time = models.DateTimeField("结束时间", null=True)

    class Meta:
        db_table = "web_status_abnormal_log"
        verbose_name = '网站警告日志'


class Web_Site_Log(models.Model):
    """
    Web运行日志
    """
    web = models.ForeignKey('web_status.Web_Site', on_delete=models.CASCADE)
    delay = models.IntegerField("延迟", default=0)
    status = models.IntegerField("状态码", default=404)
    time = models.DateTimeField("时间", auto_now_add=True)

    class Meta:
        db_table = "web_status_log"
        verbose_name = '网站运行日志'

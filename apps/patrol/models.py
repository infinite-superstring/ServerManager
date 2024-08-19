from django.db import models


class Patrol(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    status = models.CharField("状态", max_length=256)
    content = models.CharField("内容", max_length=4096)
    image_list = models.ManyToManyField('Image')
    title = models.CharField("title", max_length=256, null=False, default="无标题")
    time = models.DateTimeField("巡检时间", auto_now_add=True)

    class Meta:
        db_table = "patrol"
        db_table_comment = "巡检记录"

    class Image(models.Model):
        id = models.AutoField(primary_key=True, unique=True)
        image_hash = models.CharField(max_length=256, null=False, unique=True)

        class Meta:
            db_table = "patrol:image"
            db_table_comment = "巡检记录 - 图片"

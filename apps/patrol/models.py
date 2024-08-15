from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='./data/patrol/img')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name

class Patrol(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    status = models.CharField("状态", max_length=256)
    content = models.CharField("内容", max_length=4096)
    img = models.ForeignKey(UploadedImage, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField("title", max_length=256, null=False, default="无标题")
    time = models.DateTimeField("巡检时间", auto_now_add=True)

    class Meta:
        db_table = "patrol"
        db_table_comment = "巡检记录"

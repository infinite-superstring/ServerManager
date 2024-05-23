from django.db import models


# Create your models here.
class MessageBody:
    title: str = None
    content: str = None

    def __init__(self, title=None, content=None):
        self.title = title
        self.content = content


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('消息标题', max_length=100)
    content = models.TextField('消息内容')
    read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('新建时间', auto_now_add=True)

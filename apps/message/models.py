from django.db import models


# Create your models here.
class MessageBody:
    title: str = None
    content: str = None
    name: str = None
    recipient: list = None
    server_groups: int = None
    permission_id: int = None

    def __init__(
            self,
            title=None,
            content=None,
            name=None,
            recipient: list = None,
            server_groups: int = None,
            permission_id: int = None):
        """
        封装消息信息
        recipient 收件人ID
        server_groups 服务器群
        permission_id 权限组
        指定其中一个发件方式
        """
        self.title = title
        self.content = content
        self.name = name

        count = sum(1 for arg in [recipient, server_groups, permission_id] if arg is not None)
        if count != 1:
            raise ValueError("请指定一个发件方式")
        self.recipient = recipient
        self.server_groups = server_groups
        self.permission_id = permission_id


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('消息标题', max_length=100)
    content = models.TextField('消息内容')
    create_time = models.DateTimeField('新建时间', auto_now_add=True)


class UserMessage(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey('user_manager.User', on_delete=models.DO_NOTHING)
    message = models.ForeignKey('message.Message', on_delete=models.CASCADE)
    read = models.BooleanField('是否已读', default=False)

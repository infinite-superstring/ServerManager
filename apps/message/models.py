from django.db import models
from django.db.models import QuerySet

from apps.group.manager.models import Node_Group
from apps.permission_manager.models import Permission_groups
from apps.user_manager.models import User


# Create your models here.
class MessageBody:
    title: str = None
    content: str = None
    name: str = None
    recipient: QuerySet[User] | User = None
    node_groups: QuerySet[Node_Group] | Node_Group = None
    permission: QuerySet[Permission_groups] | Permission_groups = None
    email_sms_only: bool = False

    def __init__(
            self,
            title=None,
            content=None,
            name=None,
            recipient: QuerySet[User] | User = None,
            node_groups: QuerySet[Node_Group] | Node_Group = None,
            permission: QuerySet[Permission_groups] | Permission_groups = None,
            email_sms_only: bool = False):
        """
        封装消息信息
        recipient 用户列表
        server_groups 服务器群
        permission_id 权限组
        email_sms_only 只发送电子邮件 or 短信
        指定其中一个发件方式
        """
        self.title = title
        self.content = content
        self.name = name
        self.email_sms_only = email_sms_only

        count = sum(1 for arg in [recipient, node_groups, permission] if arg is not None)
        if count != 1:
            raise ValueError("请指定一个发件方式")
        self.recipient = recipient
        self.node_groups = node_groups
        self.permission = permission


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('消息标题', max_length=100)
    content = models.TextField('消息内容')
    create_time = models.DateTimeField('新建时间', auto_now_add=True)
    class Meta:
        db_table = 'message'
        db_table_comment = '消息'


class UserMessage(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey('user_manager.User', on_delete=models.DO_NOTHING)
    message = models.ForeignKey('message.Message', on_delete=models.CASCADE)
    read = models.BooleanField('是否已读', default=False)

    class Meta:
        db_table = 'user_message'
        db_table_comment = '用户消息'

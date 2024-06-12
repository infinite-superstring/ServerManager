import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.apps import apps
from django.db.models import QuerySet

from apps.audit.util.auditTools import write_system_log
from apps.message.models import Message
from apps.message.models import MessageBody, UserMessage
from apps.node_manager.models import Node_MessageRecipientRule, Node_Group
from apps.permission_manager.models import Permission_groups
from apps.user_manager.models import User
from util.logger import Log

"""
email 方法
"""
EMAIL_METHOD = 'email'
"""
SMS 方法
"""
SMS_METHOD = 'SMS'

# 拿到消息配置
config = apps.get_app_config('setting').get_config


def byUserGetUsername(user: User) -> str:
    """
    根据用户对象获取用户名
    """
    name = None
    if user.realName:
        name = user.realName
    elif user.userName:
        name = user.userName
    else:
        name = user.email
    return name


def __get_all_user_contact_way(way: str) -> list:
    """
    获取所有用户联系方式
    """
    if way == EMAIL_METHOD:
        return [user.email for user in User.objects.all()]
    elif way == SMS_METHOD:
        return [user.phone for user in User.objects.all()]


def get_week():
    weekday = datetime.now().weekday()  # 使用timezone.now()获取带时区意识的当前时间
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return days[weekday]


def _get_should_reception(node_group) -> QuerySet[Node_MessageRecipientRule]:
    """
    获取 现在时间段应该接收消息的用户
    """
    now = datetime.now()
    hour, minute = now.hour, now.minute
    current_time = f"{hour:02d}:{minute:02d}"
    curr_week = get_week()
    conditions = {
        f'{curr_week}': True,
        'start_time__lte': current_time,
        'end_time__gte': current_time
    }
    should_receptions = node_group.time_slot_recipient.filter(**conditions)
    should_receptions = should_receptions.distinct()
    return should_receptions


def _message_to_database(msg: MessageBody):
    """
    根据消息对象将消息存入数据库，并返回用户
    """
    if not msg.node_groups and not msg.permission and not msg.recipient:
        # 没指定发消息方式，不发送
        return None

    message_obj = Message.objects.create(title=msg.title, content=msg.content, create_time=datetime.now())

    def create_recipient(us: QuerySet[User]):
        for u in us:
            # 只发送电子邮件则不需要存储至数据库
            if msg.email_sms_only:
                UserMessage.objects.create(user=u, message=message_obj, read=False)
        return us

    def node_group_to_recipient(node_groups: Node_Group, u_list: QuerySet[User]):
        u_list = u_list | User.objects.filter(id=node_group.leader.id)
        # 节点接收人
        tsr = _get_should_reception(node_group)
        for t in tsr:
            recipients = t.recipients.all()
            u_list = u_list | recipients
        return u_list

    # 指定用户
    if msg.recipient:
        if isinstance(msg.recipient, User):
            return create_recipient(us=User.objects.filter(id=msg.recipient.id))
        else:
            return create_recipient(us=msg.recipient)
    # 指定节点组组
    if msg.node_groups:
        us_list = User.objects.none()
        if isinstance(msg.node_groups, Node_Group):
            us_list = node_group_to_recipient(msg.node_groups, us_list)
        else:
            for node_group in msg.node_groups:
                us_list = node_group_to_recipient(node_group, us_list)
        if us_list is None:
            return
        # 去重
        us_list = us_list.distinct()
        return create_recipient(us=us_list)

        # 指定权限组
    if msg.permission:
        users: QuerySet[User] = User.objects.none()
        if isinstance(msg.recipient, Permission_groups):
            users = User.objects.filter(permission_id=msg.permission.id)
        else:
            users = User.objects.filter(permission_id__in=[p.id for p in msg.permission])
        return create_recipient(us=users)


def get_email_content(msg: MessageBody, on_web_page=False):
    """
    封装消息到HTML
    """
    with open('apps/message/emailTemplates/emailTemplates.html', 'r', encoding='utf-8') as f:
        html = f.read()
        # 解析HTML
        html = html.replace('{{title}}', msg.title)
        html = html.replace('{{content}}', msg.content)
        html = html.replace('{{date}}', str(datetime.now()))
        html = html.replace('{{name}}', msg.name)
        if on_web_page:
            html = html.replace('{{on_web_page}}', 'none')
        else:
            html = html.replace('{{on_web_page}}', 'block')
        return html


def send_email(mes_obj: MessageBody, users: QuerySet[User]):
    """
    发送邮件
    """
    # 如果配置ssl连接 则开启 ssl连接
    if config().message.email_ssl:
        # 创建 stp服务器连接
        stp = smtplib.SMTP_SSL(host=config().message.email_host, port=config().message.email_port, timeout=3)
    else:
        stp = smtplib.SMTP(host=config().message.email_host, port=config().message.email_port, timeout=3)

    # 登录到服务器
    stp.login(config().message.email_username, config().message.email_password)

    for u in users:
        # 创建邮件实例
        mes_obj.recipient = u.email
        mes_obj.name = byUserGetUsername(user=u)
        content = get_email_content(mes_obj)  # 封装邮件内容
        email = MIMEMultipart()
        email.set_charset("UTF-8")
        #  封装邮件
        email.attach(MIMEText(content, 'html', 'utf-8'))
        # TODO 测试使用
        email['Subject'] = "龙芯测试平台消息通知" + mes_obj.title
        email['From'] = config().message.email_from_address
        email['To'] = u.email
        # 发送邮件
        stp.send_message(email)
    stp.quit()


def send(mes_obj: MessageBody):
    """
    发送消息
    返回用户列表
    """

    # 发送邮件
    if config().message.message_send_type == EMAIL_METHOD:
        try:
            # 邮件写到数据库
            users: QuerySet[User] = _message_to_database(mes_obj)
            if not users:
                return
            # 执行发送
            send_email(mes_obj=mes_obj, users=users)
            if mes_obj.email_sms_only:
                return None
            return users
        except smtplib.SMTPException as e:
            Log.error(e)
            raise smtplib.SMTPException
        except TimeoutError as e:
            e = "可能由端口错误发送邮件超时" + str(e)
            Log.error(e)
            raise TimeoutError
    # 发送短信
    elif config().message.message_send_type == SMS_METHOD:
        return


def send_ws(user: QuerySet[User]):
    """
    向客户端发送套接字
    """
    if not user or user is None:
        return
    for u in user:
        # 获取未读消息数量
        u_msg = UserMessage.objects.filter(user=u, read=False)
        channel_layer = get_channel_layer()
        sync_send = async_to_sync(channel_layer.group_send)
        sync_send(f"message_client_{u.id}", {"type": "newMessage", "data": u_msg.count()})


def send_err_handle(mes: str):
    """
    发送错误处理
    """
    write_system_log(level=3, module='message', content="消息发送错误,可能原因是：”" + mes + "“")

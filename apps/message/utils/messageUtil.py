from datetime import datetime
from typing import Tuple, List, Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import QuerySet

from apps.audit.util.auditTools import write_system_log
from apps.user_manager.models import User
from django.apps import apps
from apps.message.models import MessageBody, UserMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apps.user_manager.util.userUtils import get_user_by_id
from util.logger import Log
import smtplib
from apps.message.models import Message

"""
email 方法
"""
EMAIL_METHOD = 'email'
"""
SMS 方法
"""
SMS_METHOD = 'SMS'


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


def _message_to_database(msg: MessageBody):
    """
    根据消息对象将消息存入数据库，并返回用户
    """

    if not msg.server_groups and not msg.permission and not msg.recipient:
        # 没指定发消息方式，不发送
        return {}

    message_obj = Message.objects.create(title=msg.title, content=msg.content, create_time=datetime.now())

    def create_recipient(us: QuerySet[User]):
        for u in us:
            UserMessage.objects.create(user=u, message=message_obj, read=False)
        return us

    # 指定用户
    if msg.recipient:
        return create_recipient(us=msg.recipient)
    # 指定服务器组
    if msg.server_groups:
        return {}
    # 指定权限组
    if msg.permission:
        users = User.objects.filter(permission_id__in=[p.id for p in msg.permission])
        return create_recipient(us=users)


def get_email_content(msg: MessageBody, on_web_page=False):
    """
    封装消息到HTML
    """
    with open('apps/message/templates/emailTemplates.html', 'r', encoding='utf-8') as f:
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


def send(mes_obj: MessageBody):
    """
    发送消息
    """
    # 拿到消息配置
    message_config = apps.get_app_config('setting').get_config().message

    # 发送邮件
    if message_config.message_send_type == EMAIL_METHOD:
        try:

            # 邮件写到数据库
            users: QuerySet[User] = _message_to_database(mes_obj)
            if not users:
                return

            # 如果配置ssl连接 则开启 ssl连接
            if message_config.email_ssl:
                # 创建 stp服务器连接
                stp = smtplib.SMTP_SSL(host=message_config.email_host, port=message_config.email_port, timeout=3)
            else:
                stp = smtplib.SMTP(host=message_config.email_host, port=message_config.email_port, timeout=3)

            # 登录到服务器
            stp.login(message_config.email_username, message_config.email_password)

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
                email['From'] = message_config.email_from_address
                email['To'] = u.email
                # 发送邮件
                stp.send_message(email)

            stp.quit()
            return users
        except smtplib.SMTPException as e:
            Log.error(e)
            raise smtplib.SMTPException
        except TimeoutError as e:
            e = "可能由端口错误发送邮件超时" + str(e)
            Log.error(e)
            raise TimeoutError
    # 发送短信
    elif message_config.message_send_type == SMS_METHOD:
        return


def send_ws(user: QuerySet[User]):
    """
    向客户端发送套接字
    """
    if not user:
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

from datetime import datetime

from django.db.models import QuerySet

from apps.audit.util.auditTools import write_system_log
from apps.user_manager.models import User
from django.apps import apps
from apps.message.models import MessageBody, UserMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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


def __get_all_user_contact_way(way: str) -> list:
    """
    获取所有用户联系方式
    """
    if way == EMAIL_METHOD:
        return [user.email for user in User.objects.all()]
    elif way == SMS_METHOD:
        return [user.phone for user in User.objects.all()]


def _message_to_database(msg: MessageBody) -> list:
    """
    根据消息对象将消息存入数据库，并返回收件人列表
    """

    if not msg.server_groups and not msg.permission_id and not msg.recipient:
        # 没指定发消息方式，不发送
        return []

    message_obj = Message.objects.create(title=msg.title, content=msg.content, create_time=datetime.now())

    def create_recipient(us: QuerySet[User]) -> list:
        for u in us:
            UserMessage.objects.create(user=u, message=message_obj, read=False)
        return [u.email for u in us]

    # 指定用户
    if msg.recipient:
        users = User.objects.filter(id__in=msg.recipient)
        return create_recipient(us=users)
    # 指定服务器组
    if msg.server_groups:
        return []
    # 指定权限组
    if msg.server_groups:
        users = User.objects.filter(permission_id=msg.permission_id)
        return create_recipient(us=users)


def get_email_content(msg: MessageBody, on_web_page=False):
    """
    封装消息到HTML
    """

    copy_info = """
                <div
                        style="width: 600px; margin: 0 auto;  margin-top: 50px; font-size: 12px; -webkit-font-smoothing: subpixel-antialiased; text-size-adjust: 100%;">
                    <p
                            style="text-align: center; line-height: 20.4px; text-size-adjust: 100%; font-family: 'Microsoft YaHei'!important; padding: 0px !important; margin: 0px !important; color: #7e8890 !important;">
                            <span class="appleLinks">
                                Copyright © 2024 无限超弦 . 保留所有权利。</span>
                    </p>
                    <p
                            style="text-align: center;line-height: 20.4px; text-size-adjust: 100%; font-family: 'Microsoft YaHei'!important; padding: 0px !important; margin: 0px; color: #7e8890 !important; margin-top: 10px;">
                            <span class="appleLinks">
                                邮件由系统自动发送，请勿直接回复本邮件！</span>
                    </p>
                </div>
                """

    return f"""
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title></title>
</head>
<body>
<div style="font-size: 14px;">
    <div style="width: 600px; margin: 0 auto; background-color: rgb(24, 103, 192); border-radius: 3px;">
        <div style="padding: 0 15px; padding-bottom: 20px;">
            <div style="height: 72px;">
                <div>
                    <a href="#" rel="noopener"
                       style="text-decoration: none;">

                        <div style="
                        font-family: 'Arial Black', Gadget, sans-serif;
                        font-size: 20px;
                        color: white; 
                        letter-spacing: 2px; 
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.25); 
                        display: inline-block;
                        padding: 5px 10px; 
                        border-radius: 5px; 
                                ">
                            Server Manager for LoongArch
                        </div>
                    </a>
                </div>
            </div>
            <div style="background: #fff; padding: 20px 15px; border-radius: 3px;">
                <div><span style="font-size: 16px; font-weight: bold;">你好：{msg.name}</span>
                    <div style="line-height: 24px; margin-top: 10px;">
                        <div>
                            <!-- 内容 -->
                            {msg.content}
                        </div>
                    </div>
                </div>
                <p>{datetime.now()}</p>
                <div style="margin-top: 60px;margin-bottom: 10px;"><span
                        style="font-size: 13px; font-weight: bold; color: #666;">温馨提醒</span>
                    <div style="line-height: 24px; margin-top: 10px;">
                        <div style="font-size: 13px; color: #666;">使用过程中如有任何问题，请联系LIMS系统管理员。</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {copy_info if not on_web_page else ''}
</div>
</body>
</html>

    """


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
            recipients = _message_to_database(mes_obj)

            # 如果配置ssl连接 则开启 ssl连接
            if message_config.email_ssl:
                # 创建 stp服务器连接
                stp = smtplib.SMTP_SSL(host=message_config.email_host, port=message_config.email_port, timeout=3)
            else:
                stp = smtplib.SMTP(host=message_config.email_host, port=message_config.email_port, timeout=3)

            # 登录到服务器
            stp.login(message_config.email_username, message_config.email_password)

            for recipient in recipients:
                # 创建邮件实例
                mes_obj.recipient = recipient
                content = get_email_content(mes_obj)  # 封装邮件内容
                email = MIMEMultipart()
                email.set_charset("UTF-8")
                #  封装邮件
                email.attach(MIMEText(content, 'html', 'utf-8'))
                # TODO 测试使用
                email['Subject'] = "龙芯测试平台消息通知" + mes_obj.title
                email['From'] = message_config.email_from_address
                email['To'] = recipient
                # 发送邮件
                stp.send_message(email)

            stp.quit()
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


def send_err_handle(mes: str):
    """
    发送错误处理
    """
    write_system_log(level=3, module='message', content="消息发送错误,可能原因是：”" + mes + "“")

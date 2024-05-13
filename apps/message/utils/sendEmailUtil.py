from apps.audit.models import System_Log
from apps.audit.util.auditTools import write_system_log
from apps.user_manager.models import User
from django.apps import apps
from apps.message.models import MessageBody, Message
from email.message import EmailMessage
from util.logger import Log
import smtplib

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


def send(mes_obj: MessageBody):
    """
    发送消息
    """
    # 拿到消息配置
    message_config = apps.get_app_config('setting').get_config().message

    # 发送邮件
    if message_config.message_send_type == EMAIL_METHOD:
        try:

            Message.objects.create(title=mes_obj.title, content=mes_obj.content)
            recipients = __get_all_user_contact_way(message_config.message_send_type)
            email = EmailMessage()
            email.set_charset("UTF-8")
            email.set_content(mes_obj.content)

            # 如果配置ssl连接 则开启 ssl连接
            if message_config.email_ssl:
                # 创建 stp服务器连接
                stp = smtplib.SMTP_SSL(host=message_config.email_host, port=message_config.email_port)
            else:
                stp = smtplib.SMTP(host=message_config.email_host, port=message_config.email_port)

            # 登录到服务器
            stp.login(message_config.email_username, message_config.email_password)
            email['Subject'] = "龙芯测试平台消息通知" + mes_obj.title
            email['From'] = message_config.email_from_address
            email['To'] = recipients
            # 发送邮件
            stp.send_message(email)
            stp.quit()
        except smtplib.SMTPException as e:
            Log.error(e)
            raise smtplib.SMTPException
        except TimeoutError as e:
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
    print(System_Log.objects.all().values_list())

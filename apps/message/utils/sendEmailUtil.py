import time

from datetime import datetime

from apps.audit.models import System_Log
from apps.audit.util.auditTools import write_system_log
from apps.user_manager.models import User
from django.apps import apps
from apps.message.models import MessageBody, Message
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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


def __get_email_content(msg: MessageBody):
    return f"""
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>您的邮件标题</title>
</head>
<body>
<div style="font-size: 14px;">
    <br><br><br><br>
    <div style="width: 600px; margin: 0 auto; background-color: rgb(24, 103, 192); border-radius: 3px;">
        <div style="padding: 0 15px; padding-bottom: 20px;">
            <div style="height: 72px;">
                <div>
                    <a href="#" rel="noopener"
                       style="text-decoration: none;">

                        <div style="
                        font-family: 'Arial Black', Gadget, sans-serif; /* 更换为更粗的字体 */
                        font-size: 20px;
                        color: white; /* 更深邃的蓝色 */
                        letter-spacing: 2px; /* 字符间距，让文字更加清晰 */
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.25); /* 添加阴影效果 */
                        display: inline-block;
                        padding: 5px 10px; /* 添加内边距，提升质感 */
                        border-radius: 5px; /* 圆角边缘 */
                                ">
                            Server Manager for LoongArch
                        </div>
                    </a>
                </div>
            </div>
            <div style="background: #fff; padding: 20px 15px; border-radius: 3px;">
                <div><span style="font-size: 16px; font-weight: bold;">你好：</span>
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
    <div
            style="width: 600px; margin: 0 auto;  margin-top: 50px; font-size: 12px; -webkit-font-smoothing: subpixel-antialiased; text-size-adjust: 100%;">
        <p
                style="text-align: center; line-height: 20.4px; text-size-adjust: 100%; font-family: 'Microsoft YaHei'!important; padding: 0px !important; margin: 0px !important; color: #7e8890 !important;">
                <span class="appleLinks">
                    Copyright © 2024 Server Manager for LoongArch. 保留所有权利。</span>
        </p>
        <p
                style="text-align: center;line-height: 20.4px; text-size-adjust: 100%; font-family: 'Microsoft YaHei'!important; padding: 0px !important; margin: 0px; color: #7e8890 !important; margin-top: 10px;">
                <span class="appleLinks">
                    邮件由系统自动发送，请勿直接回复本邮件！</span>
        </p>
    </div>
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
            Message.objects.create(title=mes_obj.title, content=mes_obj.content)
            # 获取收件人
            recipients = __get_all_user_contact_way(message_config.message_send_type)
            recipients = ['1101658312@qq.com']

            # 如果配置ssl连接 则开启 ssl连接
            if message_config.email_ssl:
                # 创建 stp服务器连接
                stp = smtplib.SMTP_SSL(host=message_config.email_host, port=message_config.email_port)
            else:
                stp = smtplib.SMTP(host=message_config.email_host, port=message_config.email_port)

            # 登录到服务器
            stp.login(message_config.email_username, message_config.email_password)

            # 创建邮件实例
            content = __get_email_content(mes_obj)  # 封装邮件内容
            email = MIMEMultipart()
            email.set_charset("UTF-8")

            #  封装邮件
            email.attach(MIMEText(content, 'html', 'utf-8'))
            email['Subject'] = "龙芯测试平台消息通知" + mes_obj.title
            email['From'] = message_config.email_from_address
            email['To'] = ",".join(recipients)
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

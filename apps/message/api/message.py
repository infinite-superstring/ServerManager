from smtplib import SMTPServerDisconnected, SMTPAuthenticationError, SMTPException
from apps.audit.util.auditTools import write_access_log
from apps.message.models import MessageBody, Message
from util.Request import getClientIp
from util.Response import ResponseJson
from apps.message.utils.sendEmailUtil import send, send_err_handle


def send_email(message: MessageBody):
    """
    发送邮件接口
    """
    try:
        msg_obj = message
        send(msg_obj)
    except SMTPServerDisconnected as e:
        send_err_handle("连接错误，请尝试使用SSL连接")
    except SMTPAuthenticationError as e:
        """
        账号密码错误
        """
        send_err_handle("账号或密码错误,认证失败,请检查配置")
    except SMTPException as e:
        """
        可能是发送人的账号错误
        """
        send_err_handle("邮件发送地址错误,请检查配置")
    except TimeoutError as e:
        """
        端口错误
        """
        send_err_handle("邮件服务端口错误,请检查配置")
    else:
        return ResponseJson({"status": 1, "msg": "发送成功"})


def get_message_list(request):
    """
    获取消息列表
    """
    if request.method == "GET":
        write_access_log(request.session.get("userID"), getClientIp(request),
                         f"Get message list")
        mlist = Message.objects.all()
        return ResponseJson({"status": 1, "msg": "获取成功", "data": mlist.values_list()})
    else:
        return ResponseJson({"status": 0, "msg": "请求方式错误"})

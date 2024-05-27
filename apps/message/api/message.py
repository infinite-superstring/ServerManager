from datetime import datetime
from smtplib import SMTPServerDisconnected, SMTPAuthenticationError, SMTPException
from apps.audit.util.auditTools import write_access_log
from apps.message.models import MessageBody, Message, UserMessage
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_username
from util.Request import getClientIp, RequestLoadJson
from util.Response import ResponseJson
from apps.message.utils.sendEmailUtil import send, send_err_handle, get_email_content


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
        send_err_handle("邮件发送地址错误,或者端口错误,请检查配置")
    except TimeoutError as e:
        """
        端口错误
        """
        send_err_handle("邮件服务端口错误,请检查配置")
    else:
        return True


def get_message_list(request):
    """
    获取消息列表
    """

    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    write_access_log(request.session.get("userID"), getClientIp(request),
                     f"Get message list")

    user = request.session.get('user')
    user: User = get_user_by_username(user)
    method = request.GET.get('method')
    mlist = None
    if not method:
        method = 'all'
    if method == "unread":
        mlist = UserMessage.objects.filter(user_id=user.id, read=False)
    elif method == "read":
        mlist = UserMessage.objects.filter(user_id=user.id, read=True)
    elif method == "all":
        mlist = UserMessage.objects.filter(user_id=user.id)
    mlist = [{"id": i.message.id, "title": i.message.title, "content": i.message.content,
              "read": i.read, "create_time": i.message.create_time.strftime("%Y-%m-%d %H:%M:%S")} for i in mlist]
    return ResponseJson({"status": 1, "msg": "获取成功", "data": mlist})


def get_by_id(request):
    """
    根据id获取消息
    """
    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)

    msg_id = request.GET.get('id')
    user = request.session.get("user")
    user = get_user_by_username(user)
    msg = UserMessage.objects.get(user_id=user.id, message_id=msg_id)
    if msg is None:
        return ResponseJson({"status": 0, "msg": "消息不存在"})

    msg.read = True
    msg.save()

    name = None
    if user.realName:
        name = user.realName
    elif user.userName:
        name = user.userName
    else:
        name = user.email

    msg = get_email_content(MessageBody(
        title=msg.message.title,
        content=msg.message.content,
        name=name,
        recipient=[user.email],
    ),
        on_web_page=True)
    return ResponseJson({"status": 1, "msg": "获取成功", "data": msg})


def delete_by_id(request):
    """
    根据id删除消息
    """
    if request.method == "POST":
        id = request.POST.get("id")
        Message.objects.filter(id__in=id).delete()
        return ResponseJson({"status": 1, "msg": "删除成功"})
    else:
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)

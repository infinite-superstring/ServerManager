from datetime import datetime
from smtplib import SMTPException, SMTPAuthenticationError, SMTPServerDisconnected

from django.db.models import QuerySet

from apps.audit.util.auditTools import write_access_log
from apps.message.models import MessageBody, Message, UserMessage
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_username
from util.Request import getClientIp, RequestLoadJson
from util.Response import ResponseJson
from apps.message.utils.messageUtil import send, send_err_handle, get_email_content, byUserGetUsername, send_ws
from util.pageUtils import get_page_content, get_max_page


def send_email(message: MessageBody):
    """
    发送邮件接口
    """
    try:
        users = send(message)
    except SMTPServerDisconnected as e:
        send_err_handle("连接错误，请尝试使用SSL连接")
    except SMTPAuthenticationError as e:
        """
        账号或密码错误
        """
        send_err_handle("邮件服务用户名或密码错误,认证失败,请检查配置")
    except SMTPException as e:
        """
        可能是发送人的账号错误
        """
        send_err_handle("邮件发件地址错误,认证失败,请检查配置")
    except TimeoutError as e:
        """
        端口错误
        """
        send_err_handle("邮件服务端口错误,请检查配置")
    except Exception as e:
        """未知错误"""
        send_err_handle("未知错误,请检查配置")
    else:
        send_ws(users)
        return True


def get_message_list(request):
    """
    获取消息列表
    """

    # send_ws(user=User.objects.all())

    def _get_page_list(r, current_page: int, pz: int = 20) -> QuerySet:
        result_list = get_page_content(r, current_page if current_page > 1 else 1, pz)
        return result_list

    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    write_access_log(request.session.get("userID"), getClientIp(request),
                     f"Get message list")

    user = request.session.get('user')
    user: User = get_user_by_username(user)
    method = request.GET.get('method')
    curr = request.GET.get('currentPage')
    page_size = request.GET.get('pageSize', 10)
    mlist = None
    if not method != 'all' and method != 'read' and method != 'unread':
        method = 'all'
    if method == "unread":
        mlist = UserMessage.objects.filter(user_id=user.id, read=False)
    elif method == "read":
        mlist = UserMessage.objects.filter(user_id=user.id, read=True)
    elif method == "all":
        mlist = UserMessage.objects.filter(user_id=user.id)

    page_result = _get_page_list(mlist, int(curr), pz=int(page_size))
    count = mlist.count()
    max_page = get_max_page(count, int(page_size))

    result = []
    for m in page_result:
        message = Message.objects.get(id=m['message_id'])
        result.append({
            "id": message.id,
            "title": message.title,
            "content": message.content,
            "createTime": datetime.strftime(message.create_time, "%Y-%m-%d %H:%M:%S"),
            "read": m['read'],
        })
    return ResponseJson({"status": 1, "msg": "获取成功", "data": {"list": result, "maxPage": max_page}})


def get_by_id(request):
    """
    根据id获取消息
    """
    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)

    write_access_log(request.session.get("userID"), getClientIp(request),
                     f"Get message by id")

    msg_id = request.GET.get('id')
    user = request.session.get("user")
    user = get_user_by_username(user)
    msg = UserMessage.objects.get(user_id=user.id, message_id=msg_id)
    if msg is None:
        return ResponseJson({"status": 0, "msg": "消息不存在"})

    msg.read = True
    msg.save()

    name = byUserGetUsername(user)

    msg = get_email_content(MessageBody(
        title=msg.message.title,
        content=msg.message.content,
        name=name,
        recipient=QuerySet[User](),  # 空的集合
    ),
        on_web_page=True)
    return ResponseJson({"status": 1, "msg": "获取成功", "data": msg})


def get_unread(request):
    """
    获取未读消息数量
    """
    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    write_access_log(request.session.get("userID"), getClientIp(request),
                     f"获取未读消息数量")
    return ResponseJson({"status": 1, "msg": "获取成功",
                         "data": UserMessage.objects.filter(user_id=request.session.get("userID"), read=False).count()})


def delete_all(request):
    """
    删除所有已读消息
    """
    if request.method != "DELETE":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    write_access_log(request.session.get("userID"), getClientIp(request),
                     f"删除所有已读消息")
    UserMessage.objects.filter(user_id=request.session.get("userID"), read=True).delete()
    return ResponseJson({"status": 1, "msg": "删除成功"})


def read_all(request):
    """
    已读所有消息
    """
    if request.method != "PUT":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    write_access_log(request.session.get("userID"), getClientIp(request),
                     f"已读所有消息")
    UserMessage.objects.filter(user_id=request.session.get("userID"), read=False).update(read=True)
    return ResponseJson({"status": 1, "msg": "操作成功"})


def delete_by_id(request):
    """
    根据id删除消息
    """
    if request.method != "DELETE":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    write_access_log(request.session.get("userID"), getClientIp(request))
    msg_id = request.GET.get('id')
    UserMessage.objects.filter(user_id=request.session.get("userID"), message_id=msg_id).delete()

    return ResponseJson({"status": 1, "msg": "删除成功"})

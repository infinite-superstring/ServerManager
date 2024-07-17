from datetime import datetime
from smtplib import SMTPException, SMTPAuthenticationError, SMTPServerDisconnected, SMTPDataError, SMTPResponseException

from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from apps.audit.util.auditTools import write_access_log, write_audit
from apps.message.models import MessageBody, Message, UserMessage
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id
from util.Response import ResponseJson
from apps.message.utils.messageUtil import send, send_err_handle, get_email_content, byUserGetUsername, send_ws
from util.pageUtils import get_page_content, get_max_page


async def async_send(message: MessageBody):
    # return as
    await sync_to_async(send_email)(message)


def send_email(message: MessageBody):
    """
    发送邮件接口
    """
    try:
        send(message)
        return True
    except SMTPDataError as e:
        send_err_handle(f"邮件数据错误，发件人请使用合法的ASCII编码的文字: {e}")
    except SMTPServerDisconnected as e:
        send_err_handle(f"连接错误，请尝试使用SSL连接: {e}")
    except SMTPAuthenticationError as e:
        """
        账号或密码错误
        """
        send_err_handle(f"邮件服务用户名或密码错误,认证失败,请检查配置: {e}")
    except SMTPResponseException as e:
        send_err_handle(f"邮件服务返回错误码{e.smtp_code},错误信息{e.smtp_error}")
    except SMTPException as e:
        """
        可能是发送人的账号错误
        """
        send_err_handle(f"邮件发件地址错误,认证失败,请检查配置: {e}")
    except TimeoutError as e:
        """
        端口错误
        """
        send_err_handle(f"邮件服务端口错误,请检查配置: {e}")
    except Exception as e:
        """未知错误"""
        send_err_handle(f"未知错误,请检查配置: {e}")
    return False


def get_message_list(request):
    """
    获取消息列表
    """
    def _get_page_list(r, current_page: int, pz: int = 20) -> QuerySet:
        result_list = get_page_content(r, current_page if current_page > 1 else 1, pz)
        return result_list

    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user = request.session.get('userID')
    user: User = get_user_by_id(user)
    method = request.GET.get('method')
    curr = request.GET.get('currentPage')
    page_size = request.GET.get('pageSize', 10)
    mlist = None
    unread = 0
    read = 0
    total = 0
    write_access_log(
        user,
        request,
        "站内信",
        f"获取消息列表"
    )
    if not method != 'all' and method != 'read' and method != 'unread':
        method = 'all'
    if method == "unread":
        mlist = UserMessage.objects.filter(user_id=user.id, read=False).order_by('-message__create_time')
        unread = mlist.count()
    elif method == "read":
        mlist = UserMessage.objects.filter(user_id=user.id, read=True).order_by('-message__create_time')
        read = mlist.count()
    elif method == "all":
        mlist = UserMessage.objects.filter(user_id=user.id).order_by('read', '-message__create_time')
        total = mlist.count()
    page_result = _get_page_list(mlist, int(curr), pz=int(page_size))
    count = mlist.count()
    max_page = get_max_page(count, int(page_size))

    if unread == 0:
        unread = UserMessage.objects.filter(user_id=user.id, read=False).count()
    if read == 0:
        read = UserMessage.objects.filter(user_id=user.id, read=True).count()
    if total == 0:
        total = UserMessage.objects.filter(user_id=user.id).count()

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
    return ResponseJson({"status": 1, "msg": "获取成功", "data": {
        "list": result,
        "maxPage": max_page,
        'unread': unread,
        'read': read,
        'total': total,
    }})


def get_by_id(request):
    """
    根据id获取消息
    """
    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)

    msg_id = request.GET.get('id')
    user = request.session.get("userID")
    user = get_user_by_id(user)
    write_access_log(
        user,
        request,
        "站内信",
        f"根据message_id获取消息：{msg_id}"
    )
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
    send_ws(user=User.objects.filter(id=user.id), type='unread')
    return ResponseJson({"status": 1, "msg": "获取成功", "data": msg})


def get_unread(request):
    """
    获取未读消息数量
    """
    if request.method != "GET":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user = get_user_by_id(request.session.get("userID"))
    write_access_log(
        user,
        request,
        "站内信",
        f"获取未读消息数量"
    )
    return ResponseJson({
        "status": 1,
        "msg": "获取成功",
        "data": UserMessage.objects.filter(user=user, read=False).count()
    })


def delete_all(request):
    """
    删除所有已读消息
    """
    if request.method != "DELETE":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user = get_user_by_id(request.session.get("userID"))
    read_messages = UserMessage.objects.filter(user=user, read=True)
    if read_messages.count() > 0:
        count = read_messages.count()
        write_audit(
            user,
            "删除所有已读消息",
            "站内信",
            f"删除{count}条已读消息"
        )
        read_messages.delete()
        return ResponseJson({
            "status": 1,
            "msg": f"删除成功，删除了{count}条已读信息"
        })
    return ResponseJson({
        "status": 1,
        "msg": "没有已读消息"
    })


def read_all(request):
    """
    已读所有消息
    """
    if request.method != "PUT":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user = get_user_by_id(request.session.get("userID"))
    unread_messages = UserMessage.objects.filter(user=user, read=False)
    if unread_messages.count() > 0:
        count = unread_messages.count()
        write_audit(
            user,
            "已读所有消息",
            "站内信",
            f"已读了{count}条消息"
        )
        unread_messages.update(read=True)
        send_ws(user=User.objects.filter(id=request.session.get("userID")), type='unread')
        return ResponseJson({"status": 1, "msg": f"操作成功，已将{count}条信息标记为已读"})
    return ResponseJson({
        "status": 1,
        "msg": "没有未读消息"
    })


def delete_by_id(request):
    """
    根据id删除消息
    """
    if request.method != "DELETE":
        return ResponseJson({"status": 0, "msg": "请求方式错误"}, 405)
    user = get_user_by_id(request.session.get("userID"))
    msg_id = request.GET.get('id')
    write_audit(
        user,
        "删除信息",
        '站内信',
        f'message_id：{msg_id}'
    )
    UserMessage.objects.filter(user=user, message_id=msg_id).delete()

    return ResponseJson({"status": 1, "msg": "删除成功"})

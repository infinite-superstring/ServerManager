# 修改用户信息
import base64
import hashlib
import os

from asgiref.sync import async_to_sync
from django.apps import apps
from django.http import FileResponse
from django.views.decorators.http import require_POST

from apps.user_manager.models import User as Users
from apps.user_manager.util.userUtils import get_user_by_id, write_user_new_password_to_database, \
    verify_username_and_password, username_exists
from apps.auth.utils.authCodeUtils import user_otp_is_binding
from apps.auth.utils.otpUtils import verify_otp
from util.asgi_file import async_file_response, get_file_response
from util.base64Util import get_file_size
from util.passwordUtils import verifyPasswordRules
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.logger import Log
from apps.audit.util.auditTools import write_audit, write_access_log, write_file_change_log, write_system_log
from apps.permission_manager.util.permission import groupPermission

config = apps.get_app_config('setting').get_config
avatar_save_path = os.path.join(os.getcwd(), "data", "avatar")


@require_POST
def setPassword(req):
    """
    设置密码
    :param req:
    :return:
    """
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"})
    userId = req.session.get("userID")
    data = req_json.get("data")
    oldPassword = data.get("oldPassword")
    newPassword = data.get("newPassword")
    code = data.get("code")
    if not (userId or data or oldPassword or newPassword):
        return ResponseJson({"status": -1, "msg": "参数不完整"})
    User = get_user_by_id(userId)
    if not verify_otp(User, code):
        return ResponseJson({"status": 0, "msg": "操作验证失败，请检查您的手机令牌"})
    pv, pv_msg = verifyPasswordRules(newPassword, config().security.password_level)
    if not pv:
        return ResponseJson({"status": 0, "msg": f"新密码格式不合规（{pv_msg}）"})
    if not verify_username_and_password(User, oldPassword):
        return ResponseJson({"status": 0, "msg": "原密码不正确"})
    write_user_new_password_to_database(userId, newPassword)
    write_audit(
        userId,
        "设置密码",
        "用户信息编辑",
        ""
    )
    return ResponseJson({"status": 1, "msg": "密码修改成功"})


def getUserInfo(req):
    """
    获取用户信息
    :param req:
    :return:
    """

    user = get_user_by_id(req.session.get("userID"))
    User_Permission = groupPermission(user.permission) if user.permission else None
    write_access_log(user, req, "用户信息", "获取用户信息")
    return ResponseJson({"status": 1, "data": {
        "id": user.id,
        "userName": user.userName,
        "realName": user.realName,
        'enableOTP': user_otp_is_binding(user),
        "email": user.email,
        "group": User_Permission.get_group_name() if User_Permission else None,
        "permissions": User_Permission.get_permissions_list() if User_Permission else None,
    }})


@require_POST
def setUserInfo(req):
    """
    设置用户信息
    :param req:
    :return:
    """
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    userId = req.session.get("userID")
    data = req_json.get("data")
    if not userId or not data:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    User = get_user_by_id(userId)
    userName = data.get("userName")
    email = data.get("email")
    if (userName and userName != User.userName) and username_exists(userName):
        return ResponseJson({"status": 0, "msg": "用户名已被他人使用"})
    write_audit(
        User,
        "更新用户名",
        "用户信息编辑",
        f"{User.userName}-->{userName}")
    User.userName = userName
    req.session["user"] = userName
    if email and email != User.email:
        users = Users.objects.filter(email=email)
        if users.count() >= 1:
            return ResponseJson({"status": 0, "msg": "邮箱已被使用过啦"})
        write_audit(
            User,
            "更新电子邮箱",
            "用户信息编辑",
            f"{User.email}-->{email}")
        User.email = email
    User.save()
    return ResponseJson({"status": 1, "msg": "成功", "data": {
        "userName": User.userName,
        "realName": User.realName,
        "email": User.email,
    }})


# 头像上传
@require_POST
def uploadAvatar(req):
    """
    头像上传
    :param req:
    :return: JSON
    """
    try:
        req_json = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": "JSON解析失败"}, 400)
    userId = req.session.get("userID")
    data = req_json.get("data")
    if not data:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    avatarImgBase64 = data.get("avatarImg")
    avatarImgHash = data.get("avatarHash")
    if not avatarImgBase64 or not avatarImgHash:
        return ResponseJson({"status": -1, "msg": "参数不完整"}, 400)
    if get_file_size(avatarImgBase64) > 1024 * 1024 * 0.25:
        return ResponseJson({"status": -1, "msg": "大小超出范围"}, 400)
    if not os.path.exists(avatar_save_path):
        os.makedirs(avatar_save_path)
    if os.path.exists(os.path.join(avatar_save_path, f"{avatarImgHash}")):
        User = get_user_by_id(req.session.get("userID"))
        if avatarImgHash != User.avatar:
            User.avatar = avatarImgHash
            User.save()
            write_audit(
                userId,
                "上传头像",
                "用户信息编辑",
                f"头像md5: {avatarImgHash}(文件已存在，跳过写入文件)"
            )
        return ResponseJson({"status": 1, "msg": "上传成功"})
    dataBytes = base64.b64decode(avatarImgBase64.split(",")[1])
    with open(os.path.join(avatar_save_path, f"{avatarImgHash}"), "wb+") as f:
        md5 = hashlib.md5()
        md5.update(dataBytes)
        saveFileMd5 = md5.hexdigest()
        if saveFileMd5 != avatarImgHash:
            Log.warning(f"Md5验证失败(发送时：{avatarImgHash} 接收时：{saveFileMd5})")
            write_system_log(
                2,
                "用户信息编辑->头像上传",
                f"头像Md5验证失败(发送时：{avatarImgHash} 接收时：{saveFileMd5})"
            )
            try:
                os.remove(os.path.join("avatar", f"{avatarImgHash}"))
            except Exception as err:
                Log.error(err)
            return ResponseJson({
                "status": 0,
                "msg": f"头像文件校验失败"
            }, 400)
        Log.debug("头像上传Md5验证成功")
        f.write(dataBytes)
        User = get_user_by_id(userId)
        User.avatar = avatarImgHash
        User.save()
        write_audit(
            userId,
            "上传头像",
            "用户信息编辑",
            f"头像md5: {saveFileMd5}"
        )
        write_file_change_log(
            userId,
            "保存文件(头像)",
            os.path.join("avatar", f"{avatarImgHash}")
        )
        return ResponseJson({
            "status": 1,
            "msg": "上传成功"
        })


def getAvatar(req):
    """
    获取用户头像
    :param req:
    :return: Image
    """
    userId = req.session.get("userID")

    User = get_user_by_id(userId)
    write_access_log(userId, req, "用户信息", "获取用户头像")
    if not User.avatar:
        return get_file_response('public/avatar.png')
    if os.path.exists(os.path.join(avatar_save_path, User.avatar)):
        return get_file_response(os.path.join(avatar_save_path, User.avatar))

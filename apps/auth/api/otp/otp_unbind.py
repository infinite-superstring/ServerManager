from django.http import HttpRequest, HttpResponse

from apps.auth.utils.authCodeUtils import user_otp_is_binding
from apps.user_manager.util.userUtils import get_user_by_id
from util.Response import ResponseJson


def send_email_code(request: HttpRequest) -> HttpResponse:
    """
    解绑:发送邮箱验证码
    """
    uid = request.session['userID']
    user = get_user_by_id(uid)
    if not user_otp_is_binding(user):
        return ResponseJson({
            'status': 0,
            'msg': '您未绑定OTP令牌!'
        })
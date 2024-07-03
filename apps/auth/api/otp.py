from django.http import HttpRequest, HttpResponse

from apps.user_manager.util.userUtils import get_user_by_id
from apps.auth.utils.otpUtils import check_otp
from util.result import api_error, success, error


def check_otp_input(request: HttpRequest) -> HttpResponse:
    """检查用户输入的OTP"""
    uid = request.session['userID']
    user = get_user_by_id(uid)
    if not request.method == 'GET':
        return api_error("请求方法不正确", 405)
    otp_code = request.GET.get("code", None)
    if not otp_code:
        return api_error("参数不完整")
    return success() if check_otp(user, otp_code) else error("验证失败，请检查您的验证码是否正确")
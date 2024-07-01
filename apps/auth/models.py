import pyotp
from django.db import models
from apps.user_manager.models import User


# Create your models here.

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40, unique=True)
    scanned = models.BooleanField(default=False)

    class Meta:
        db_table = 'otp'
        db_table_comment = '时间验证码'

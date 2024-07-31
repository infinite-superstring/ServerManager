from django.db import models

# Create your models here.

class Node_Group(models.Model):
    """节点组"""
    id = models.AutoField("组ID", primary_key=True)
    name = models.CharField("组名", max_length=100, unique=True, null=False)
    description = models.CharField("节点组简介", max_length=100, null=True)
    leader = models.ForeignKey("user_manager.User", on_delete=models.DO_NOTHING)
    time_slot_recipient = models.ManyToManyField(
        "Node_MessageRecipientRule",
        related_name='time_slot_recipient_mappings'
    )

    class Meta:
        db_table = 'node_groups'
        db_table_comment = '节点组列表'


class Node_MessageRecipientRule(models.Model):
    """消息接收人"""
    id = models.AutoField("ID", primary_key=True)
    monday = models.BooleanField("星期一", null=False)
    tuesday = models.BooleanField("星期二", null=False)
    wednesday = models.BooleanField("星期三", null=False)
    thursday = models.BooleanField("星期四", null=False)
    friday = models.BooleanField("星期五", null=False)
    saturday = models.BooleanField("星期六", null=False)
    sunday = models.BooleanField("星期日", null=False)
    start_time = models.TimeField("开始时间", null=False)
    end_time = models.TimeField("结束时间", null=False)
    recipients = models.ManyToManyField("user_manager.User", related_name='node_message_recipients_mapping')

    class Meta:
        db_table = 'node_message_recipient'
        db_table_comment = "节点消息接收人"
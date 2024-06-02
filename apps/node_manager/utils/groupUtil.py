from datetime import datetime

from apps.node_manager.models import Node_MessageRecipientRule, Node_Group
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id, uid_exists
from util.logger import Log


def node_group_id_exists(group_id):
    return Node_Group.objects.filter(id=group_id).exists()

def get_node_group_by_id(group_id):
    return Node_Group.objects.get(id=group_id)

def create_message_recipient_rule(
        week: list,
        start_time: str,
        end_time: str,
        users: list[User]) -> Node_MessageRecipientRule:
    """
    创建消息接收人
    :param week: 星期
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param users: 接收用户
    """
    rule = Node_MessageRecipientRule.objects.create(
        monday=True if "monday" in week else False,
        tuesday=True if "tuesday" in week else False,
        wednesday=True if "wednesday" in week else False,
        thursday=True if "thursday" in week else False,
        friday=True if "friday" in week else False,
        saturday=True if "saturday" in week else False,
        sunday=True if "sunday" in week else False,
        start_time=start_time,
        end_time=end_time,
    )
    for uid in users:
        if not uid_exists(uid):
            Log.warning(f"用户ID{uid}不存在")
            continue
        rule.recipients.add(get_user_by_id(uid))
    return rule


def create_message_recipient_rules(data: list) -> list[Node_MessageRecipientRule]:
    """
    根据列表创建消息发送规则
    """
    temp = []
    for item in data:
        temp.append(create_message_recipient_rule(
            item.get("week"),
            item.get("start_time"),
            item.get("end_time"),
            item.get("users")
        ))
    return temp

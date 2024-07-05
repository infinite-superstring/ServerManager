from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.node_manager.models import Node_MessageRecipientRule, Node_Group, Node
from apps.user_manager.models import User
from apps.user_manager.util.userUtils import get_user_by_id, uid_exists
from util.logger import Log


def node_group_id_exists(group_id):
    return Node_Group.objects.filter(id=group_id).exists()


def get_node_group_by_id(group_id):
    return Node_Group.objects.get(id=group_id)


def get_group_nodes(group):
    return Node.objects.filter(group=group)


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
    for user in users:
        Log.debug(user)
        if not uid_exists(user):
            Log.warning(f"用户ID{user}不存在")
            continue
        rule.recipients.add(get_user_by_id(user))
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


class GroupUtil:
    __group: Node_Group

    def __init__(self, group: Node_Group):
        self.__group = group

    def get_node_list(self):
        """获取组中的所有节点"""
        return Node.objects.filter(group=self.__group)

    def add_node(self, node: Node):
        """向组中添加节点"""
        node.group = self.__group
        node.save()

    def remove_node(self, node: Node):
        """删除组中的一个节点"""
        node.group = None
        node.save()

    def remove_all_nodes(self):
        """删除组中所有的节点"""
        groups = self.get_node_list()
        for group in groups:
            self.remove_node(group)

    def send_event_to_all_nodes(self, event: str, data: dict, exclude: list[Node] = None):
        """
        向所有节点实例发送事件
        :param event: 事件名 对应节点客户端WebSocket实例中的方法名
        :param data: 载荷数据
        :param exclude: 排除的节点实例
        """
        if exclude is None:
            exclude = []

        group_nodes = self.get_node_list()
        channel_layer = get_channel_layer()
        for node in group_nodes:
            if node in exclude:
                Log.debug(f"Node {node.name}({node.uuid}) is already in the excluded list, skip the send event")
                continue
            # if not node.online:
            #     Log.debug(f"Node {node.name}({node.uuid}) is offline and will skip send event")
            #     continue
            async_to_sync(channel_layer.group_send)(
                f"NodeClient_{node.uuid}",
                {**{'type': event}, **data}
            )

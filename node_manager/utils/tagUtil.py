from node_manager.models import Node_Tag, Node
from util.logger import Log


def add_tags(tags: list) -> list[Node_Tag]:
    """将未拥有的Tag加入到数据库中,并返回列表中所有的Tag实例"""
    temp = []
    for tag in tags:
        if not Node_Tag.objects.filter(tag_name=tag).exists():
            Node_Tag.objects.create(tag_name=tag)
        temp.append(Node_Tag.objects.filter(tag_name=tag).first())
    return temp


def get_tag_by_name(tag_name: str) -> list[str]:
    """按名称搜索Tag"""
    temp = []
    tags = Node_Tag.objects.filter(tag_name__icontains=tag_name)
    if tags:
        for tag in tags:
            temp.append(tag.tag_name)
    return temp


@Log.catch
def get_node_tags(node_id: int) -> list[str]:
    """根据节点获取所有Tag"""
    node = Node.objects.get(uuid=node_id)
    return node.tags.all().values_list('tag_name', flat=True)

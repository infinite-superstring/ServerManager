from apps.permission_manager.models import *
from util.logger import Log


def group_id_exists(gid):
    return Permission_groups.objects.filter(id=gid).exists()

def get_group_by_id(gid):
    if not group_id_exists(gid):
        Log.error(f'Group id {gid} does not exist.')
        return None
    return Permission_groups.objects.get(id=gid)
from apps.group_task.models import GroupTask_Cycle


def createCycle(cycle: dict):
    """
    创建周期对象
    """
    cycle_obj = GroupTask_Cycle()
    cycle_obj.time = cycle.get('time', '00:00')
    cycle_obj.sunday = cycle.get('sunday', False)
    cycle_obj.monday = cycle.get('monday', False)
    cycle_obj.tuesday = cycle.get('tuesday', False)
    cycle_obj.wednesday = cycle.get('wednesday', False)
    cycle_obj.thursday = cycle.get('thursday', False)
    cycle_obj.friday = cycle.get('friday', False)
    cycle_obj.saturday = cycle.get('saturday', False)
    cycle_obj.save()
    return cycle_obj

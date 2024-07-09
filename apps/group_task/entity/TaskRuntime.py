from io import TextIOWrapper

from apps.group_task.models import Group_Task_Audit


class TaskRuntime:
    group_task_audit: Group_Task_Audit = None
    result_uuid = None
    task_dir = None
    start_time = None
    file_stream: TextIOWrapper = None

    def __init__(self, group_task_audit: Group_Task_Audit, result_uuid, task_dir, start_time, file_stream):
        self.group_task_audit = group_task_audit
        self.result_uuid = result_uuid
        self.task_dir = task_dir
        self.start_time = start_time
        self.file_stream = file_stream

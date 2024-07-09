import os.path
from datetime import datetime

from django.apps import apps
from django.core.cache import cache

from apps.group_task.entity.TaskRuntime import TaskRuntime
from apps.group_task.models import GroupTask, Group_Task_Audit
from apps.group_task.utils import group_task_util
from apps.node_manager.models import Node


class GroupTaskResultUtil:
    """
    节点执行结果对象，用于处理任务执行结果
    """
    __node_uuid = None
    __save_base_dir: str = ''
    __map: dict = {str: TaskRuntime}

    def __init__(self, node_uuid):
        self.__node_uuid = node_uuid

    async def handle_task_start(self, data: dict):
        task_uuid = data.get('uuid')
        start_time = data.get('timestamp')
        process_id = data.get('mark')
        if not task_uuid:
            raise ValueError('任务uuid 不能为空')
        self.__save_base_dir = apps.get_app_config('node_manager').group_task_result_save_dir
        task_dir = os.path.join(
            self.__save_base_dir,
            task_uuid,
            self.__node_uuid
        )
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)
        #     生成结果唯一UUID
        result_uuid = group_task_util.by_key_get_uuid(
            task_uuid + self.__node_uuid + process_id
        )
        audit = await Group_Task_Audit. \
            objects. \
            acreate(group_task=await GroupTask.objects.aget(uuid=task_uuid),
                    node=await Node.objects.aget(uuid=self.__node_uuid), statr_time=start_time,
                    end_time=None, uuid=result_uuid, )
        cache.set(f'group_task_executing_{task_uuid}_{self.__node_uuid}', start_time, 60)
        file_stream = open(os.path.join(task_dir, str(result_uuid)), 'w+', encoding='utf-8')
        self.__map[process_id] = TaskRuntime(audit, result_uuid, task_dir, start_time, file_stream)

    async def handle_task_output(self, data: dict):
        """
        处理任务输出时
        """
        task_uuid = data.get('uuid')
        process_id = data.get('mark')
        start_time = cache.get(f'group_task_executing_{task_uuid}_{self.__node_uuid}')
        m: TaskRuntime = self.__map.get(process_id)
        if not start_time:
            m.group_task_audit.status = 'error'
            m.group_task_audit.end_time = datetime.now()
            raise ValueError('任务未开始,或已超时')
        cache.set(f'group_task_executing_{task_uuid}_{self.__node_uuid}', start_time, 60)
        line = data.get('line')
        if line:
            print(line)
            m.file_stream.write(f'{line}\n')

    async def handle_task_stop(self, data: dict):
        """
        处理任务停止时
        """
        task_uuid = data.get('uuid')
        process_id = data.get('mark')
        code = data.get('code')
        timestamp = data.get('timestamp')
        m: TaskRuntime = self.__map.get(process_id)
        m.file_stream.write(f"[END {code}]")
        m.file_stream.close()
        m.group_task_audit.status = code
        m.group_task_audit.end_time = datetime.fromtimestamp(timestamp)
        await m.group_task_audit.asave()
        cache.delete(f'group_task_executing_{task_uuid}_{self.__node_uuid}')

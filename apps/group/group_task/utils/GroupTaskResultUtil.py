import os.path
from datetime import datetime

from django.apps import apps
from django.core.cache import cache

from apps.group.group_task.entity.TaskRuntime import TaskRuntime
from apps.group.group_task.models import GroupTask, Group_Task_Audit
from apps.group.group_task.utils import group_task_util
from apps.node_manager.models import Node
from util.logger import Log


class GroupTaskResultUtil:
    """
    节点执行结果对象，用于处理任务执行结果
    """
    __node_uuid = None
    __save_base_dir: str = 'data'
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
            os.getcwd(),
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
        task: GroupTask = await GroupTask.objects.filter(uuid=task_uuid).afirst()
        audit = None
        if task:
            if task.exec_count:
                if int(task.exec_count) <= 0:
                    task.enable = False
                    await task.asave()
                    Log.warning(f'任务:{task.name}执行次数为{task.exec_count},已执行完成,并关闭任务!')
                    return
            audit = await Group_Task_Audit. \
                objects. \
                acreate(group_task=task,
                        node=await Node.objects.aget(uuid=self.__node_uuid), statr_time=start_time,
                        end_time=None, uuid=result_uuid, )
        cache.set(f'group_task_executing_{task_uuid}_{self.__node_uuid}', start_time, 60)
        file_path = os.path.join(task_dir, str(result_uuid))
        file_stream = None
        # file_stream = open(file_path, 'a+', encoding='utf-8')
        self.__map[process_id] = TaskRuntime(audit, result_uuid, task_dir, start_time, file_stream, file_path)

    async def handle_task_output(self, data: dict):
        """
        处理任务输出时
        """
        task_uuid = data.get('uuid')
        process_id = data.get('mark')
        start_time = cache.get(f'group_task_executing_{task_uuid}_{self.__node_uuid}')
        m: TaskRuntime = self.__map.get(process_id)
        if not m:
            raise ValueError('任务不存在' + process_id)
        if not start_time:
            m.group_task_audit.status = 'error'
            m.group_task_audit.end_time = datetime.now()
            raise ValueError('任务未开始,或已超时')
        cache.set(f'group_task_executing_{task_uuid}_{self.__node_uuid}', start_time, 60)
        line = data.get('line')
        if line:
            group_task_util.write_file(m.file_path, f'{line}\n')
            # with open(m.file_path, 'a+', encoding='utf-8') as stream:
            #     stream.write(f'{line}\n')
            #     print(stream.readline())
            #     stream.close()
            # m.file_stream.write(f'{line}\n')
            # print(m.file_stream.readline())

    async def handle_task_stop(self, data: dict):
        """
        处理任务停止时
        """
        task_uuid = data.get('uuid')
        process_id = data.get('mark')
        code = data.get('code')
        error = data.get('error')
        timestamp = data.get('timestamp')
        m: TaskRuntime = self.__map.get(process_id)
        group_task_util.write_file(m.file_path, f"[进程返回值:{code}]")
        if error:
            group_task_util.write_file(m.file_path, f'\n执行命令时发生错误:{error}')
        # m.file_stream.write(f"[进程返回值:{code}]")
        # m.file_stream.close()
        if m.group_task_audit:
            m.group_task_audit.status = code
            m.group_task_audit.end_time = datetime.fromtimestamp(timestamp)
            await m.group_task_audit.asave()
        cache.delete(f'group_task_executing_{task_uuid}_{self.__node_uuid}')

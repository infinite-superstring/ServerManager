import os.path

from django.apps import apps
from django.core.cache import cache

from apps.group.commandExecution.models import Cluster_ExecuteResult, Cluster_Execute
from apps.group.group_task.utils import group_task_util
from apps.node_manager.models import Node


class GroupCommandManager:
    """
    集群指令管理器
    """
    __node_uuid = None
    __save_base_dir: str
    __redis_key: str = 'group_command_run_'
    __map: dict[str, dict] = {}

    def __init__(self, node_uuid):
        self.__node_uuid: int = node_uuid
        self.__save_base_dir = apps.get_app_config('node_manager').group_command_result_save_dir

    async def start(self, data: dict):
        uuid = data.get('uuid')
        timestamp = data.get('timestamp')
        if not uuid:
            raise Exception('集群指令运行时UUID为空')
        # 唯一结果ID
        result_uuid = group_task_util.by_key_get_uuid(
            uuid + self.__node_uuid + timestamp
        )
        # 文件存储地址
        file_path = os.path.join(
            os.getcwd(),
            self.__save_base_dir,
            str(result_uuid)
        )

        self.__map[uuid] = {
            'result_uuid': result_uuid,
            'file_path': file_path,
            'data': data
        }
        cache.set(f'{self.__redis_key}{uuid}', data, 60)

    async def runtime(self, data: dict):
        if not self._check(data):
            return
        uuid = data.get('uuid')
        map_data = self.__map[uuid]
        file_path = map_data.get('file_path')
        line = data.get('line')
        if line:
            group_task_util.write_file(file_path, f'{line}\n')
        cache.set(f'{self.__redis_key}{uuid}', data, 60)

    async def stop(self, data: dict):
        if not self._check(data):
            return
        uuid = data.get('uuid')
        map_data = self.__map[uuid]
        file_path = map_data.get('file_path')
        code = data.get('code')
        error = data.get('error')
        timestamp = data.get('timestamp')
        group_task_util.write_file(file_path, f'[进程返回值{code}]')
        if error:
            group_task_util.write_file(file_path, f'\n[执行命令时发生错误{error}]')
        await Cluster_ExecuteResult.objects.acreate(
            result_uuid=self.__map[uuid].get('result_uuid'),
            node=await Node.objects.aget(uuid=self.__node_uuid),
            task=await Cluster_Execute.objects.aget(uuid=uuid),
            status_code=code,
            timestamp=timestamp
        )
        cache.delete(f'{self.__redis_key}{uuid}')

    async def _check(self, data: dict):
        uuid = data.get('uuid')
        if not uuid:
            raise Exception('集群指令运行时UUID为空')
        map_data = self.__map[uuid]
        if not map_data:
            raise Exception('这个指令不存在:' + uuid)
        cache_data = cache.get(f'{self.__redis_key}{uuid}')
        if not cache_data:
            raise Exception('指令不存在或运行超时:' + uuid)
        return True

from apps.group.file_send.models import File_DistributionTask, FileDistribution_FileList


def exists_task_by_uuid(uuid):
    return File_DistributionTask.objects.filter(uuid=uuid).exists()

def get_task_by_uuid(uuid):
    """
    通过UUID获取任务实例
    """
    return File_DistributionTask.objects.get(uuid=uuid)

def get_task_file_list(task: File_DistributionTask):
    """
    获取任务文件列表
    """
    return FileDistribution_FileList.FileName.objects.filter(task=task)

def exists_file_by_task(task: File_DistributionTask, file_hash: str):
    """
    检查任务下是否有该文件
    """
    return task.files.all().filter(file_hash=file_hash).exists()

def get_task_file_name(task: File_DistributionTask, file_hash: str):
    """
    根据任务获取对应的文件名
    """
    return FileDistribution_FileList.objects.filter(file_hash=file_hash).file_name.all().filter(task=task).first().name
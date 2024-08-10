from django.apps import apps

from util.logger import Log
from apps.setting.entity.Config import config as configObj
from apps.audit.util.auditTools import write_system_log


# 加载配置文件到对象
@Log.catch
def loadConfig(config: configObj) -> configObj:
    settings = apps.get_model('setting', 'Settings').objects.all()
    for item in settings:
        settingKeySplit = item.Settings.split('.')
        if hasattr(config, settingKeySplit[0]):
            config_obj = getattr(config, settingKeySplit[0])
            settingKeys = settingKeySplit[-1:]
            annotations = config_obj.__annotations__
            for index, split in enumerate(settingKeys):
                if index == len(settingKeys) - 1:
                    value = item.value
                    # 专门处理布尔值的转换
                    if annotations.get(split) == bool:
                        if value.lower() == 'false':
                            value = False
                        else:
                            value = True
                    else:
                        value = annotations.get(split)(value)  # 其他类型的转换
                    setattr(config_obj, split, value)
                elif hasattr(config_obj, split):
                    config_obj = getattr(config_obj, split)
    Log.success("配置已加载到内存")
    return config


# 保存对象到数据库中
@Log.catch
def saveConfig(obj: configObj) -> configObj:
    from apps.setting.models import Settings
    for item1Key, item1Value in obj.__dict__.items():
        temp = item1Key + "."
        for item2Key, item2Value in item1Value.__dict__.items():
            temp += item2Key
            settings = Settings.objects.filter(Settings=temp).first()
            if settings:
                settings.value = str(item2Value)
                Log.debug(f"key:{temp} | value:{settings.value} | type:{type(settings.value)}")
                settings.save()
            else:
                Settings.objects.create(Settings=temp, value=str(item2Value))
            temp = item1Key + "."
    Log.success("配置已写入至数据库")
    return loadConfig(obj)


# 将字典转换到对象
def dictToConfig(data: dict) -> configObj:
    """
    :param data: 数据字典
    :return: 带数据的对象
    """
    temp_config = configObj()
    for key1 in data.keys():
        if hasattr(temp_config, key1):
            temp = getattr(temp_config, key1)
            item = data.get(key1)
            annotations = temp.__annotations__
            for key2 in item.keys():
                if not hasattr(temp, key2):
                    Log.warning(f"{key2} Does not exist ")
                    continue
                if type(item[key2]) == annotations.get(key2):
                    setattr(temp, key2, annotations.get(key2)(item.get(key2)))
                else:
                    Log.warning(f"{key1}.{key2} Value Type Error! {type(item[key2])} != {annotations.get(key2)}")
                    write_system_log(3, "系统设置", f"保存设置{key1}.{key2}数据类型错误，应为{type(item[key2])}实为{annotations.get(key2)}")
        else:
            continue
    return temp_config

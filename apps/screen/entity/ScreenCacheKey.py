class ScreenCacheKey:
    """
    缓存键
    """

    class AlarmKey:
        """
        告警类型键
        """
        cpu = 'cpu'
        memory = 'memory'
        disk = 'disk'
        network = 'network'

    node_count = 'screen:node_count'
    user_count = 'screen:user_count'
    on_line_count = 'screen:node_on_line_count'
    alarm_count = 'screen:node_alarming_count'
    tasking_count = 'screen:node_tasking_count'

    average_load = 'screen:node_average_load'
    host_status = 'screen:node_host_status'
    memory = 'screen:node_memory'
    network = 'screen:node_network'
    cpu = 'screen:node_cpu'

    alarm_key = AlarmKey()

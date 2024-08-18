class BaseStatus:
    host_status = None
    average_load = None
    # 内存使用率
    memory = None
    #     网络流量
    network = None
    #     cpu使用率
    cpu = None

    def __init__(self):
        self.host_status: list = []
        self.average_load: dict = {}
        self.memory: dict = {}
        self.network: dict = {}
        self.cpu: dict = {}

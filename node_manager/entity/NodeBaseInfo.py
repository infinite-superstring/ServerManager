class CpuInfo:
    """CPU信息"""
    # 架构
    architecture: str
    # 线程数
    threads: int
    # 核心数
    cores: int


class NodeBaseInfo:
    """节点基础数据"""
    # 系统
    system: str
    # 系统版本
    system_release: str
    # 系统编译版本
    system_build_version: str
    # 主机名
    hostname: str
    # 启动时间
    boot_time: float
    # 内存总量
    memory: int
    # CPU信息
    cpu: CpuInfo

    def __init__(self):
        self.cpu = CpuInfo()

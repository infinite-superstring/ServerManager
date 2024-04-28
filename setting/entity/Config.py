
class config:
    base = None
    camera = None
    record = None
    gpio = None

    def __init__(self):
        self.base = base()
        self.camera = camera()
        self.record = record()
        self.gpio = gpio()


# 基础配置
class base:
    # HID设备串口
    HID_Serial: str = None
    # USB磁盘设备
    USB_Device: str = None
    # USB磁盘设备挂载地址
    USB_MountDirectory: str = None
    # 采集卡ID
    camera: int = None
    # 启动录制
    record: bool = None
    # Session超时时间
    sessionExpiry: int = None

# 采集卡配置
class camera:
    # 亮度
    brightness: int = None
    # 饱和度
    colorfulness: int = None
    # 曝光
    exposure: int = None
    # 帧率
    fps: int = None
    # 高度
    height: int = None
    # 色调
    tonal: int = None
    # 更新阈值
    updateDisplayChange: float = None
    # 宽度
    width: int = None
    

# GPIO配置
class gpio:
    HDD_LED: int = None
    Power_Btn: int = None
    Power_LED: int = None
    Restart_Btn: int = None
    UsbDisk_EN: int = None
    UsbDisk_Switch: int = None
    mode: str = None
    pollingRate: float = None
    

# 录制配置
class record:
    fps: int = None
    maxFile: int = None
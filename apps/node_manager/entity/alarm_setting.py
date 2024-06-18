class AlarmSetting:
    enable: bool = None
    delay_seconds: int = None
    cpu = None
    memory = None
    network = None
    disk: list[disk] = []

    def __init__(self, enable, delay_seconds, cpu, memory, network, disk):
        self.enable = enable
        self.delay_seconds = delay_seconds
        self.cpu = cpu
        self.memory = memory
        self.network = network
        self.disk = disk


class cpu:
    enable: bool = None
    threshold: int = None

    def __init__(self, enable, threshold):
        self.enable = enable
        self.threshold = threshold

    def is_enable(self):
        return self.enable and self.threshold


class memory:
    enable: bool = None
    threshold: int = None

    def __init__(self, enable, threshold):
        self.enable = enable
        self.threshold = threshold

    def is_enable(self):
        return self.enable and self.threshold


class network:
    enable: bool = None
    send_threshold: int = None
    receive_threshold: int = None

    def __init__(self, enable, send_threshold, receive_threshold):
        self.enable = enable
        self.send_threshold = send_threshold
        self.receive_threshold = receive_threshold

    def is_enable(self):
        return self.enable and self.send_threshold and self.receive_threshold


class disk:
    device: str = None
    threshold: int = None

    def __init__(self, device, threshold):
        self.device = device
        self.threshold = threshold

    def is_enable(self):
        return self.device and self.threshold

class AuthRestrictions:
    enable: bool
    method: int
    value: str

    def __init__(self, enable: bool, method: int, value: str):
        self.enable = enable
        self.method = method
        self.value = value


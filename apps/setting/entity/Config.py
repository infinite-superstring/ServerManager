class config:
    base = None
    security = None
    node = None
    node_usage = None
    node_default_alarm_setting = None
    message = None
    web_status = None
    terminal_audit = None

    def __init__(self):
        self.base = base()
        self.security = security()
        self.node = node()
        self.node_usage = node_usage()
        self.node_default_alarm_setting = node_default_alarm_setting()
        self.message = message()
        self.web_status = web_status()
        self.terminal_audit = terminal_audit()


# 基础配置
class base:
    # 服务器Token
    server_token: str = None
    # 站点URL
    website_url: str = None
    # 站点名称
    website_name: str = None
    # Session超时时间
    session_expiry: int = None


# 安全性
class security:
    # 密码安全等级
    password_level: int = None
    # 强制绑定OTP令牌
    force_otp_bind: bool = None
    # 消息验证码重发时间(秒)
    auth_code_resend_interval: int = None
    # 消息验证码超时时间(分)
    auth_code_timeout: int = None
    # 消息验证码长度
    auth_code_length: int = None
    # 登录失败次数限制
    login_error_count: int = None
    # 限制登陆时长(分钟)
    login_expiry: int = None


# 节点配置
class node:
    # 超时下线时间（毫秒）
    timeout: int = None
    # 心跳包时间（毫秒）
    heartbeat_time: int = None


class node_usage:
    # 运行数据提交间隔（秒）
    upload_data_interval: int = None
    # 存储粒度（分）
    data_save_interval: int = None
    # 使用数据存储时限（天）
    data_storage_time: int = None


# 节点默认告警设置
class node_default_alarm_setting:
    # 启用告警设置
    enable: bool = None
    # 告警延迟时间
    delay_seconds: int = None
    # 告警间隔时间
    interval: int = None
    # 启用CPU告警
    cpu__enable: bool = None
    # CPU告警阈值
    cpu__threshold: int = None
    # 启用内存告警
    memory__enable: bool = None
    # 内存告警阈值
    memory__threshold: int = None
    # 网络告警启用
    network__enable: bool = None
    # 网络告警-发送数据量
    network__send_threshold: int = None
    # 网络告警-接收数据量
    network__receive_threshold: int = None


# 消息设置
class message:
    message_send_type: str = None
    # 邮件发送方式
    email_method: str = None
    # 邮件服务器地址
    email_host: str = None
    # 邮件服务器端口
    email_port: int = None
    # 邮件用户名
    email_username: str = None
    # 邮件密码
    email_password: str = None
    # 是否使用SSL
    email_ssl: bool = None
    # 邮件发件地址
    email_from_address: str = None
    # 邮件发件人
    email_from_name: str = None


class web_status:
    heartbeat: int = None
    timeout: int = None



# 终端审计设置
class terminal_audit:
    # 启用终端审计
    enable: bool = None
    # 禁用Tab键
    disable_tab_key: bool = None
    # 警告命令列表
    warn_command_list: str = None
    # 危险命令列表
    danger_command_list: str = None
    # 禁止命令列表
    disable_command_list: str = None
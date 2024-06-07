class config:
    base = None
    node = None
    message = None

    def __init__(self):
        self.base = base()
        self.node = node()
        self.node_usage = node_usage()
        self.message = message()


# 基础配置
class base:
    # 服务器Token
    server_token: str = None
    # Session超时时间
    session_expiry: int = None
    # 登录失败次数显示
    login_error_count: int = None
    # 限制登陆时长 分钟
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

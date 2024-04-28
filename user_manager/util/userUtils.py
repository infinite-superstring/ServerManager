from user_manager.models import User


def get_user_by_id(uid) -> User:
    """
    根据用户id获取用户实例
    :param uid:
    :return: User
    """
    return User.objects.get(id=uid)


def get_user_by_username(username) -> User:
    return User.objects.get(userName=username)


def verify_username_and_password(username: str, password: str) -> bool:
    return User.objects.filter(userName=username, password=password).exists()


def get_all_user() -> set[User]:
    """
    获取所有用户实例
    :return: set[User]
    """
    return User.objects.all()

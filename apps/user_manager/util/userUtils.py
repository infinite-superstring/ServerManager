from apps.user_manager.models import User
from util.passwordUtils import verify_password, encrypt_password
from util.logger import Log


def get_user_by_id(uid) -> bool | User:
    """
    根据用户id获取用户实例
    :param uid:
    :return: User
    """
    if not uid_exists(uid):
        Log.error(f'User ID {uid} does not exist')
        return False
    return User.objects.get(id=uid)


def get_user_by_username(username) -> User:
    return User.objects.get(userName=username)

def username_exists(username) -> bool:
    return User.objects.filter(userName=username).exists()


def real_name_exists(real_name) -> bool:
    return User.objects.filter(realName=real_name).exists()


def email_exists(email) -> bool:
    return User.objects.filter(email=email).exists()


def uid_exists(uid) -> bool:
    return User.objects.filter(id=uid).exists()


async def uid_aexists(uid) -> bool:
    return await User.objects.filter(id=uid).aexists()


def verify_username_and_password(user, password: str) -> bool:
    """
        验证用户密码
        :param user: 用户实例或uid
        :param password: 密码
        """

    user_object: User
    if isinstance(user, int):
        user_object = User.objects.get(id=user)
    elif isinstance(user, str):
        if not username_exists(user): return False
        user_object = User.objects.get(userName=user)
    elif isinstance(user, User):
        user_object = user
    else:
        return False

    return verify_password(user_object.password, password, user_object.passwordSalt)


def write_user_new_password_to_database(user, password: str):
    """
    写入用户新密码到数据库
    :param user: 用户实例或uid
    :param password: 密码
    """
    user_object: User
    if isinstance(user, int):
        user_object = User.objects.get(id=user)
    elif isinstance(user, User):
        user_object = user
    else:
        return False
    hashed_password, salt = encrypt_password(password)
    user_object.password = hashed_password
    user_object.passwordSalt = salt
    user_object.save()
    return user_object


def get_all_user() -> set[User]:
    """
    获取所有用户实例
    :return: set[User]
    """
    return User.objects.all()

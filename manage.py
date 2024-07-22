#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from util.logger import Log


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoongArch-ServerManager.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)



if __name__ == '__main__':
    if not os.path.exists(".init") and 'runserver' in sys.argv:
        Log.info('Initializing server...')
        os.system('python manage.py makemigrations')
        os.system('python manage.py migrate')
        os.system('python manage.py initial_data')
        exit(0)
    if not os.path.exists("data"):
        os.mkdir("data")
    # init_show.log_list[random.randint(0,len(init_show.log_list))-1]()
    print("""
前端：https://github.com/infinite-superstring/ServerManager-UI
后端：https://github.com/infinite-superstring/ServerManager-Panel
节点：https://github.com/infinite-superstring/ServerManager-Node""")
    main()

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import random
import sys
from util import init_show
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
    # init_show.logo2()
    init_show.log_list[random.randint(0,len(init_show.log_list))-1]()
    print("""
前端：https://github.com/infinite-superstring/ServerManager-UI
后端：https://github.com/infinite-superstring/ServerManager-Panel
节点：https://github.com/infinite-superstring/ServerManager-Node""")
    main()

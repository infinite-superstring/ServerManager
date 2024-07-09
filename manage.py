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
    Log.info("""
 _____        __ _       _ _          _____                           _        _             
|_   _|      / _(_)     (_) |        / ____|                         | |      (_)            
  | |  _ __ | |_ _ _ __  _| |_ ___  | (___  _   _ _ __   ___ _ __ ___| |_ _ __ _ _ __   __ _ 
  | | | '_ \|  _| | '_ \| | __/ _ \  \___ \| | | | '_ \ / _ \ '__/ __| __| '__| | '_ \ / _` |
 _| |_| | | | | | | | | | | ||  __/  ____) | |_| | |_) |  __/ |  \__ \ |_| |  | | | | | (_| |
|_____|_| |_|_| |_|_| |_|_|\__\___| |_____/ \__,_| .__/ \___|_|  |___/\__|_|  |_|_| |_|\__, |
                                                 | |                                    __/ |
                                                 |_|                                   |___/ 
前端：https://github.com/infinite-superstring/ServerManager-UI
后端：https://github.com/infinite-superstring/ServerManager-Panel
节点：https://github.com/infinite-superstring/ServerManager-Node
    """)
    main()

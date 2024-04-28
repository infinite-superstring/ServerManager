from django.apps import AppConfig
# from app.devices.camera import camera
# from app.devices.ch9329 import ch3929

import sys

STARTAPP = "runserver" in sys.argv

if STARTAPP:
    pass
    # if len(main_config.get("main").get("serial")) != 0:
    #     HID = ch3929(main_config.get("main").get("serial"))
    # else:
    #     raise RuntimeError("HID串口未填写")

    # if main_config.get("main").get("camera") is not None:
    #     cameraObj = camera(main_config.get("main").get("camera"))
    # else:
    #     raise RuntimeError("摄像头id未填写")

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        pass


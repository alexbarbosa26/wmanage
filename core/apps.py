from django.apps import AppConfig
from django.http import request

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):     
        from . import updater
        updater.start()

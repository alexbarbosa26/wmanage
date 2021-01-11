from django.apps import AppConfig

class CadastroConfig(AppConfig):
    name = 'cadastro'

    def ready(self):        
        from . import updater
        updater.start()

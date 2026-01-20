from django.apps import AppConfig
import sys

class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'

    def ready(self):
        if 'runserver' in sys.argv:
            from .utils import cleanup_unused_files
            try:
                cleanup_unused_files()
            except:
                pass
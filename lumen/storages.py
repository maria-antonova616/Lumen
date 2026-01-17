import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ImproperlyConfigured

# Пакет для работы с Cloudinary
try:
    from cloudinary_storage.storage import MediaCloudinaryStorage
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False


class CloudinaryFallbackStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active_storage = None

    def _check_cloudinary_available(self):
        if not CLOUDINARY_AVAILABLE:
            return False
        
        # Проверяем, настроены ли ключи в settings.py
        cloudinary_settings = getattr(settings, 'CLOUDINARY_STORAGE', {})
        if not all([cloudinary_settings.get('CLOUD_NAME'), 
                    cloudinary_settings.get('API_KEY'), 
                    cloudinary_settings.get('API_SECRET')]):
            return False
            
        # Проверяем доступность API Cloudinary
        try:
            # Это должен быть легкий запрос, чтобы не вызывать таймауты
            cloudinary.api.ping() 
            return True
        except Exception as e:
            print(f"Cloudinary API ping failed: {e}") # Логируем ошибку
            return False

    def _get_active_storage(self):
        if self._active_storage is None:
            if self._check_cloudinary_available():
                self._active_storage = MediaCloudinaryStorage()
                print("Using Cloudinary Storage")
            else:
                # Если Cloudinary недоступен, используем локальное хранилище
                self._active_storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
                print("Using FileSystem Storage")
        return self._active_storage

    def __getattr__(self, name):
        # Перехватываем все обращения к методам и свойствам и перенаправляем их
        # к активному хранилищу (Cloudinary или FileSystem)
        return getattr(self._get_active_storage(), name)

    def _save(self, name, content):
        # Для метода _save нам нужно явно вызвать _save у активного хранилища
        return self._get_active_storage()._save(name, content)
        
    def _open(self, name, mode='rb'):
        # Для метода _open
        return self._get_active_storage()._open(name, mode)

    # Добавьте другие необходимые методы, если они не будут работать через __getattr__
    # Например, если storage.url() вызывается напрямую, а не через model.field.url
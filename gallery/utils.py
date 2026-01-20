import os
from django.conf import settings
from gallery.models import Photo

def cleanup_unused_files():
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        return

    db_files = set()
    for photo in Photo.objects.all():
        if photo.image:
            db_files.add(os.path.normpath(photo.image.path))
        if photo.thumbnail:
            db_files.add(os.path.normpath(photo.thumbnail.path))

    for root, dirs, files in os.walk(media_root):
        for file in files:
            file_path = os.path.normpath(os.path.join(root, file))
            if file_path not in db_files:
                try:
                    os.remove(file_path)
                    print(f"Deleted orphaned file: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                except:
                    pass

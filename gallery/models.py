from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
import uuid, os, shutil

class Gallery(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photographer_galleries",
        verbose_name="Фотограф"
    )
    is_public = models.BooleanField(default=False, verbose_name="Публичный доступ")
    is_active = models.BooleanField(default=True, verbose_name="Активна (прием лайков)")
    is_common_likes = models.BooleanField(default=False, verbose_name="Общие лайки")
    clients_see_others = models.BooleanField(default=False, verbose_name="Клиенты видят чужие")
    viewers_see_likes = models.BooleanField(default=False, verbose_name="Зрители видят лайки")
    max_selection_count = models.PositiveIntegerField(default=30, verbose_name="Лимит выбора (на человека)")
    total_selection_limit = models.PositiveIntegerField(default=0, verbose_name="Общий лимит")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="Срок действия")
    def __str__(self):
        return self.title
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
class GalleryAccess(models.Model):
    ROLE_CHOICES = [
        ('CLIENT', 'Клиент (Выбор фото)'),
        ('VIEWER', 'Зритель (Только просмотр)'),
    ]
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='access_list')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gallery_accesses')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VIEWER')
    original_role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Последний просмотр")
    class Meta:
        unique_together = ('gallery', 'user')
class GalleryInvite(models.Model):
    ROLE_CHOICES = [
        ('CLIENT', 'Клиент (Выбор фото)'),
        ('VIEWER', 'Зритель (Только просмотр)'),
    ]
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='invites')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VIEWER')
    usage_limit = models.PositiveIntegerField(default=0)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def is_valid(self):
        if self.usage_limit > 0 and self.usage_count >= self.usage_limit:
            return False
        return True
class Photo(models.Model):
    STATUS_CHOICES = [
        ('UNVIEWED', 'Не просмотрено'),
        ('APPROVED', 'Одобрено'),
        ('PROCESSING', 'В обработке'),
        ('READY', 'Готово'),
    ]
    gallery = models.ForeignKey(Gallery, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='photos/thumbs/', blank=True, null=True)
    sequence_number = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UNVIEWED')
    photographer_note = models.TextField(blank=True, verbose_name="Примечание фотографа")
    original_filename = models.CharField(max_length=255, blank=True, verbose_name="Оригинальное имя")

    class Meta:
        ordering = ['sequence_number']
class ClientChoice(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='choice')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_choices")
    is_liked = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('photo', 'client')
class ProcessingStage(models.Model):
    gallery = models.ForeignKey(Gallery, related_name='stages', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['order']

@receiver(post_delete, sender=Photo)
def delete_photo_files(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)

@receiver(post_delete, sender=Gallery)
def delete_gallery_folder(sender, instance, **kwargs):
    pass
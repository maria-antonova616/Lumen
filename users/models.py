from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        PHOTOGRAPHER = 'PHOTOGRAPHER', 'Photographer'
        CLIENT = 'CLIENT', 'Client'
    role = models.CharField(max_length=50, choices=Role.choices)
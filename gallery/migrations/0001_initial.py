import uuid
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
    ]
    operations = [
        migrations.CreateModel(
            name='ClientChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_liked', models.BooleanField(default=False)),
                ('is_viewed', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('is_public', models.BooleanField(default=False, verbose_name='Публичный доступ')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна (прием лайков)')),
                ('is_common_likes', models.BooleanField(default=False, verbose_name='Общие лайки')),
                ('clients_see_others', models.BooleanField(default=False, verbose_name='Клиенты видят чужие')),
                ('viewers_see_likes', models.BooleanField(default=False, verbose_name='Зрители видят лайки')),
                ('max_selection_count', models.PositiveIntegerField(default=30, verbose_name='Лимит выбора (на человека)')),
                ('total_selection_limit', models.PositiveIntegerField(default=0, verbose_name='Общий лимит')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(verbose_name='Срок действия')),
            ],
        ),
        migrations.CreateModel(
            name='GalleryAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('CLIENT', 'Клиент (Выбор фото)'), ('VIEWER', 'Зритель (Только просмотр)')], default='VIEWER', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('last_viewed_at', models.DateTimeField(blank=True, null=True, verbose_name="Последний просмотр")),
            ],
        ),
        migrations.CreateModel(
            name='GalleryInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('role', models.CharField(choices=[('CLIENT', 'Клиент (Выбор фото)'), ('VIEWER', 'Зритель (Только просмотр)')], default='VIEWER', max_length=20)),
                ('usage_limit', models.PositiveIntegerField(default=0)),
                ('usage_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/%Y/%m/%d/')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='photos/thumbs/')),
                ('sequence_number', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('UNVIEWED', 'Не просмотрено'), ('APPROVED', 'Одобрено'), ('PROCESSING', 'В обработке'), ('READY', 'Готово')], default='UNVIEWED', max_length=20)),
            ],
            options={
                'ordering': ['sequence_number'],
            },
        ),
        migrations.CreateModel(
            name='ProcessingStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('completed', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]

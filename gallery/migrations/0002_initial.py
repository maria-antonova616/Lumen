import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('gallery', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name='clientchoice',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_choices', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gallery',
            name='photographer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photographer_galleries', to=settings.AUTH_USER_MODEL, verbose_name='Фотограф'),
        ),
        migrations.AddField(
            model_name='galleryaccess',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_list', to='gallery.gallery'),
        ),
        migrations.AddField(
            model_name='galleryaccess',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_accesses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='galleryinvite',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='gallery.gallery'),
        ),
        migrations.AddField(
            model_name='photo',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='gallery.gallery'),
        ),
        migrations.AddField(
            model_name='clientchoice',
            name='photo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice', to='gallery.photo'),
        ),
        migrations.AddField(
            model_name='processingstage',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='gallery.gallery'),
        ),
        migrations.AlterUniqueTogether(
            name='galleryaccess',
            unique_together={('gallery', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='clientchoice',
            unique_together={('photo', 'client')},
        ),
    ]
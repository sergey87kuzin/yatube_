# Generated by Django 2.2.6 on 2021-04-03 09:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0008_auto_20210325_1758'),
    ]

    operations = [
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avatars', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
        ),
    ]
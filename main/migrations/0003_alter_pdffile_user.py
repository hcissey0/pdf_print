# Generated by Django 4.2.7 on 2023-12-24 05:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_alter_pdffile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdffile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='file', to=settings.AUTH_USER_MODEL),
        ),
    ]
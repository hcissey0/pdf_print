from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.db.utils import NotSupportedError
import os
from django.conf import settings
import unicodedata
import shutil
import string

# Create your models here.

def ascii_filename(instance, filename):
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    cleaned_filename = ''.join(
        c
        for c in cleaned_filename
        if c in string.ascii_letters + string.digits + '_-.'
    )
    return 'uploads/' + cleaned_filename

class PdfFile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='file')
    name = models.CharField(max_length=256)
    file = models.FileField(upload_to=ascii_filename)

    def clean(self):
        super().clean()
        if not self.file.name.endswith('.pdf'):
            raise NotSupportedError('Only PDF files allowed')

    def delete(self):
        full_path = str(settings.BASE_DIR) + str(self.file.url)
        if os.path.exists(full_path):
            os.remove(full_path)
        split_path = full_path[:-4] + '/'
        if os.path.exists(split_path):
            shutil.rmtree(split_path)
        return super().delete()

    def __str__(self):
        return str(self.id) + "-" + self.name

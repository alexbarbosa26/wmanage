from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.

class Csv(models.Model):
    file_name = models.FileField(upload_to='csvs', validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    uploaded = models.DateTimeField(auto_now=True)
    activated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"File id: {self.id}"

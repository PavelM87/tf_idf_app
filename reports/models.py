from django.db import models
from django.core.validators import FileExtensionValidator


class File(models.Model):
    
    file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['txt'])])

    def __str__(self) -> str:
        return self.file.name
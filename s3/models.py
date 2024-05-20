from django.db import models
import datetime
import magic
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Upload(models.Model):
    def validate_mime_type(value):
        if value.size > 1024*1024*10:
            raise ValidationError(u'File size must be less than 10MB.')
        supported_types=['application/pdf','image/jpeg','image/jpg','text/plain']
        m = magic.Magic(mime=True)
        mime_type = m.from_buffer(value.file.read(2048))
        value.file.seek(0)
        if mime_type not in supported_types:
            raise ValidationError(u'Unsupported file type.')

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(default="", max_length=40)
    file = models.FileField(validators=[validate_mime_type])

    PRIORITY_CHOICES = (
        (1, 'Lowest Priority'),
        (2, 'Low Priority'),
        (3, 'Moderate Priority'),
        (4, 'High Priority'),
        (5, 'Highest Priority'),
    )

    STATUS_CHOICES = (
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    )
    user_comment = models.TextField(default="")
    admin_comment = models.TextField(default="No comment yet")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)





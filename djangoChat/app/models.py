from django.db import models

# Create your models here.
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    
    class Meta:
        ordering = ["-id"] #역순 정렬 위해서
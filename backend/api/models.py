from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Event(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    note = models.TextField(max_length=300, default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event")
    
    def __str__(self):
        return self.title 
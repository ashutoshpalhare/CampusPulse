from django.db import models

class Entry(models.Model):
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=80, default='Core')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models

# Create your models here.

class Links(models.Model):
    link = models.CharField(max_length=1000, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Links"

    def __str__(self):
        return f'{self.link}'

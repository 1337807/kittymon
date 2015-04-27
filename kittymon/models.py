from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Kitty(models.Model):
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.url

class UserKitty(models.Model):
    user = models.ForeignKey(User)
    kitty = models.ForeignKey(Kitty)

from django.db import models

# Create your models here.
class Result(models.Model):
    sentiment = models.CharField(max_length=250)
    classification = models.CharField(max_length=10)
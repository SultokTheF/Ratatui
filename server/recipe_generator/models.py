from django.db import models

class GeneratedRecipe(models.Model):
    title = models.CharField(max_length=255)
    ingredients = models.TextField()
    directions = models.TextField()
from django.db import models

# Create your models here.
class Mvp(models.Model):
    name = models.CharField(max_length=100)
    one_liner = models.CharField(max_length=100)
    description = models.TextField()

    # since projects usually consist of multiple repositories, we need to store the github project url
    # instead of the individual repository url
    github_project_url = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

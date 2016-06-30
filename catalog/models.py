from django.db import models


class MainEmployees(models.Model):
    file = models.FileField(upload_to='main_employees', blank=True, null=True)

    @staticmethod
    def get_file():
        obj, created = MainEmployees.objects.get_or_create(pk=1)
        return obj

from django.db import models
from django.utils import timezone

# Create your models here.


class TrafficLightObjects(models.Model):
    num_CO = models.CharField(max_length=20)
    type_controller = models.CharField(max_length=10)
    ip_adress = models.CharField(max_length=12)
    adress = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    connection = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.num_CO} + {self.type_controller}'

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]


class SaveConfigFiles(models.Model):
    source = models.CharField(max_length=20)
    file = models.FileField(upload_to='conflicts/configs/', null=True, verbose_name='config_file')
    time_create = models.DateTimeField(default=timezone.now)
    controller_type = models.CharField(max_length=20, db_index=True, default='undefind')

    def __repr__(self):
        return self.file.name


class SaveConflictsTXT(models.Model):
    source = models.CharField(max_length=20)
    file = models.FileField(upload_to='conflicts/txt/', null=True, verbose_name='txt_files')
    time_create = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return self.file.name


class ControllerManagement(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    # num_visible_hosts = models.CharField(max_length=2, blank=False, null=False, default='1')
    num_visible_hosts = models.IntegerField(default=1, blank=True)
    data = models.TextField(unique=True)
    # data = models.JSONField(unique=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    category = models.IntegerField()
    user_name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


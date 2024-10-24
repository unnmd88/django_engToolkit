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


class TrafficLightObjects(models.Model):
    number = models.IntegerField(default=0000, unique=True)
    description = models.CharField(max_length=30)
    type_controller = models.CharField(max_length=10)
    group = models.IntegerField(default=0)
    ip_adress = models.CharField(max_length=12, unique=True)
    adress = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    connection = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.number} + {self.type_controller}'

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]
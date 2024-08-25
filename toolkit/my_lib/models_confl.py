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




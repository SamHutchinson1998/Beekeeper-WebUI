from django.db import models

# Create your models here.

DEVICE_TYPES = (
    ('router','ROUTER'),
    ('pc','PC'),
    ('switch','SWITCH'),
    ('mlswitch','MULTI-LAYER SWITCH')
)

class DiskImage(models.Model):
    name = models.TextField()
    devicetype = models.CharField(max_length=8,choices=DEVICE_TYPES, default='pc')
    disk_image = models.FileField(upload_to='disk_images/')
    #image = models.ImageField()

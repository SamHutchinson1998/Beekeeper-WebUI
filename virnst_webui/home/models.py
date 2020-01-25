from django.db import models

# Create your models here.

DEVICE_TYPES = (
    ('router','ROUTER'),
    ('pc','PC'),
    ('switch','SWITCH'),
    ('mlswitch','MULTI-LAYER SWITCH')
)

class DiskImage(models.model):
    name = models.TextField()
    devicetype = models.CharField(choices=DEVICE_TYPES, default='pc')
    disk_image = models.FileField(upload_to='disk_images/')
    image = models.ImageField()
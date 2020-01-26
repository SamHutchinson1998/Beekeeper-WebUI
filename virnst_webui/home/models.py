from django.db import models
from django.forms import ModelForm

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

class ImageForm(ModelForm):
  class Meta:
    model = DiskImage
    fields = ['name', 'devicetype', 'disk_image']

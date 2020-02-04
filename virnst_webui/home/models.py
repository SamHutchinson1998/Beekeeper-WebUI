from django.db import models
from django import forms

# Create your models here.

DEVICE_TYPES = (
  ('router','router'),
  ('pc','pc'),
  ('switch','switch'),
  ('mlswitch','multi-layer switch'),
  ('server', 'server')
)

RAM_SIZES = (
  ('256','256mb'),
  ('512','512mb'),
  ('1024','1024mb'),
  ('1536','1536mb'),
  ('2048','2048mb'),
  ('4096','4096mb')
)

CPU_LIST = (
  ('1','1'),
  ('2','2'),
  ('3','3'),
  ('4','4')
)

class DiskImage(models.Model):
  name = models.CharField(max_length=100)
  devicetype = models.CharField(max_length=8,choices=DEVICE_TYPES, default='pc')
  disk_image = models.FileField(upload_to='disk_images/')

class VirtualMachine(models.Model):
  name = models.CharField(max_length=100)
  ram = models.CharField(max_length=8)
  disk_size = models.IntegerField()
  cpus = models.IntegerField()
  disk_image = models.ForeignKey(DiskImage, on_delete=models.CASCADE)

class ImageForm(forms.ModelForm):
  class Meta:
    model = DiskImage
    fields = ['name', 'devicetype', 'disk_image']

class VirtualMachineForm(forms.ModelForm):
  class meta:
    model = VirtualMachine
    fields = ['name', 'ram', 'disk_size', 'cpus']

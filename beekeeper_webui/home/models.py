from django.db import models
from django import forms
from secrets import token_urlsafe

# Create your models here.

DEVICE_TYPES = (
  ('router','router'),
  ('pc','pc'),
  ('switch','switch'),
  ('mlswitch','multi-layer switch'),
  ('server', 'server')
)

class DiskImage(models.Model):
  name = models.CharField(max_length=100)
  devicetype = models.CharField(max_length=8,choices=DEVICE_TYPES, default='pc')
  disk_image = models.FileField(upload_to='disk_images/')

class VirtualMachine(models.Model):
  name = models.CharField(max_length=100,default="vm_name")
  ram = models.CharField(max_length=8)
  disk_size = models.IntegerField()
  cpus = models.IntegerField()
  cell_id = models.IntegerField(default='0')
  disk_image = models.ForeignKey(DiskImage, on_delete=models.CASCADE)
  token = models.CharField(max_length=22,default=token_urlsafe(16))

class ImageForm(forms.ModelForm):
  class Meta:
    model = DiskImage
    fields = ['name', 'devicetype', 'disk_image']

class VirtualMachineForm(forms.ModelForm):
  class Meta:
    model = VirtualMachine
    fields = ['name','ram', 'disk_size', 'cpus', 'cell_id','disk_image']

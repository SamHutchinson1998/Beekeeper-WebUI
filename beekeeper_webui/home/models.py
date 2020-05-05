from django.db import models
from django import forms
import os
# Create your models here.

DEVICE_TYPES = (
  ('router','router'),
  ('pc','pc'),
  ('switch','switch'),
  ('mlswitch','multi-layer switch'),
  ('server', 'server')
)

class DiskImage(models.Model):
  name = models.CharField(max_length=100, unique=True)
  devicetype = models.CharField(max_length=8,choices=DEVICE_TYPES, default='pc')
  disk_image = models.FileField(upload_to='disk_images/')

  def extension(self):
    name, extension = os.path.splitext(self.disk_image.name)
    if extension.lower() == '.iso':
      return 'iso'
    if extension.lower() == '.qcow2':
      return 'qcow2'
    return 'other'

class Device(models.Model):
  name = models.CharField(max_length=100,default="vm_name", unique=True)
  ram = models.CharField(max_length=8)
  disk_size = models.IntegerField()
  cpus = models.IntegerField()
  cell_id = models.IntegerField(default='0')
  disk_image = models.ForeignKey(DiskImage, on_delete=models.SET_NULL)
  token = models.CharField(max_length=64,default='0')
  console_port = models.IntegerField(default='10000')

class EthernetPorts(models.Model):
  virtual_machine = models.ForeignKey(Device, on_delete=models.CASCADE)
  #connected_to = models.CharField(max_length=10)
  mac_address = models.CharField(max_length=48)

class EthernetCable(models.Model):
  name = models.CharField(max_length=100,default="bridge_name",unique=True)
  source = models.ForeignKey(EthernetPorts, related_name='source', null=True, on_delete=models.SET_NULL)
  target = models.ForeignKey(EthernetPorts, related_name='target', null=True, on_delete=models.SET_NULL)
  cell_id = models.IntegerField(default='0')

class ImageForm(forms.ModelForm):
  class Meta:
    model = DiskImage
    fields = ['name', 'devicetype', 'disk_image']

class DeviceForm(forms.ModelForm):
  class Meta:
    model = Device
    fields = ['name','ram', 'disk_size', 'cpus', 'cell_id','disk_image']
    labels = {
      'ram': 'RAM (MB)',
      'disk_size': 'Disk Size (GB)'
    }

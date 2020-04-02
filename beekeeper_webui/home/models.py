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

class DiskImage(models.Model):
  name = models.CharField(max_length=100, unique=True)
  devicetype = models.CharField(max_length=8,choices=DEVICE_TYPES, default='pc')
  disk_image = models.FileField(upload_to='disk_images/')

class VirtualMachine(models.Model):
  name = models.CharField(max_length=100,default="vm_name", unique=True)
  ram = models.CharField(max_length=8)
  disk_size = models.IntegerField()
  cpus = models.IntegerField()
  cell_id = models.IntegerField(default='0')
  disk_image = models.ForeignKey(DiskImage, on_delete=models.CASCADE)
  token = models.CharField(max_length=64,default='0')

class EthernetPort(models.Model):
  virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)
  #connected_to = models.CharField(max_length=10)
  mac_address = models.CharField(max_length=48)

class EthernetCable(models.Model):
  name = models.CharField(max_length=100,default="bridge_name",unique=True)
  source = models.ForeignKey(EthernetPort, related_name='source', null=True, on_delete=models.CASCADE)
  target = models.ForeignKey(EthernetPort, related_name='target', null=True, on_delete=models.CASCADE)
  cell_id = models.IntegerField(default='0')
  
  # Automatically delete any ethernet ports associated with the EthernetCable
  def delete(self):
    if self.source:
      self.source.delete()
    if self.target:
      self.target.delete()


class EthernetPortForm(forms.ModelForm):
  class Meta:
    model = EthernetPort
    fields = ['virtual_machine', 'mac_address']

class ImageForm(forms.ModelForm):
  class Meta:
    model = DiskImage
    fields = ['name', 'devicetype', 'disk_image']

class VirtualMachineForm(forms.ModelForm):
  class Meta:
    model = VirtualMachine
    fields = ['name','ram', 'disk_size', 'cpus', 'cell_id','disk_image']
    labels = {
      'ram': 'RAM (MB)',
      'disk_size': 'Disk Size (GB)'
    }

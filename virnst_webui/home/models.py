from django.db import models
from django import forms

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

class ImageForm(forms.ModelForm):
  class Meta:
    model = DiskImage
    fields = ['name', 'devicetype', 'disk_image']
    widgets = {
      'name': forms.TextInput(
        attrs={
          'class': 'form-control'
        }
      )
      'devicetype': forms.CharField(
        attrs={
          'class': 'form-control'
        }
      )
      'disk_image': forms.FileField(
        attrs={
          'class': 'form-control'
        }
      )
    }

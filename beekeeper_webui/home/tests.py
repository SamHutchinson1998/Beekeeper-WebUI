from django.test import TestCase
from .models import Device, DiskImage

# Models tests

def create_image(self, name, devicetype, diskimage):
  return DiskImage.objects.create(name=name, devicetype=devicetype, disk_image=diskimage)

class DiskImageTest(TestCase):

  def test_image_creation(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    # copy - test the uniqueness of the name field
    self.assertTrue(isinstance(image,DiskImage))

class DeviceTest(TestCase):

  def create_device(self, name, ram, disk_size, cpus, cell_id, disk_image, token, console_port):
    return Device.objects.create(name=name, ram=ram, disk_size=disk_size, cpus=cpus, cell_id=cell_id, disk_image=disk_image, token=token, console_port=console_port)
  
  def test_device_creation(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = self.create_device('test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    self.assertTrue(isinstance(device,Device))

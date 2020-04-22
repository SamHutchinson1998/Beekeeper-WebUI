from django.test import TestCase, TransactionTestCase
from django.db import IntegrityError
from .models import Device, DiskImage, EthernetPorts, EthernetCable
from .models import EthernetPortsForm, ImageForm, DeviceForm

# Table of contents

# 1. Models tests
# 2. Forms tests
# 3. Views tests

# Models tests

def create_image(self, name, devicetype, diskimage):
  return DiskImage.objects.create(name=name, devicetype=devicetype, disk_image=diskimage)

def create_device(self, name, ram, disk_size, cpus, cell_id, disk_image, token, console_port):
  return Device.objects.create(name=name, ram=ram, disk_size=disk_size, cpus=cpus, cell_id=cell_id, disk_image=disk_image, token=token, console_port=console_port)

def create_ethernet_ports(self, virtual_machine, mac_address):
  return EthernetPorts.objects.create(virtual_machine=virtual_machine, mac_address=mac_address)

class DiskImageTest(TestCase):

  def test_image_creation(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    # copy - test the uniqueness of the name field
    self.assertTrue(isinstance(image,DiskImage))

class DeviceTest(TestCase):
  
  def test_device_creation(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    self.assertTrue(isinstance(device,Device))

class EthernetPortsTest(TestCase):
    
  def test_ethernet_ports_creation(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    ethernet_port = create_ethernet_ports(self, device, 'MA:CA:DD:RE:SS:XD')
    self.assertTrue(isinstance(ethernet_port, EthernetPorts))

class EthernetCableTest(TestCase):

  def create_ethernet_cable(self, name, source, target, cell_id):
    return EthernetCable.objects.create(name=name, source=source, target=target, cell_id=cell_id)

  def test_ethernet_cable(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    source_device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    source = create_ethernet_ports(self, source_device, 'MA:CA:DD:RE:SS:XD')
    target_device = create_device(self, 'test_device_2', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    target = create_ethernet_ports(self, target_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = self.create_ethernet_cable('test-cable', source, target, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_source(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    target_device = create_device(self, 'test_device_2', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    target = create_ethernet_ports(self, target_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = self.create_ethernet_cable('test-cable', None, target, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_target(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    source_device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    source = create_ethernet_ports(self, source_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = self.create_ethernet_cable('test-cable', source, None, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_source_target(self):
    ethernet_cable = self.create_ethernet_cable('test-cable', None, None, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

# Forms tests

class ImageFormTest(TransactionTestCase):

  def test_valid_image_form(self):
    image = create_image(self, 'test_image_2', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    data = {'name': image.name, 'devicetype': image.devicetype, 'disk_image': image.disk_image}
    form = ImageForm(data)
    self.assertTrue(form.is_valid())

  def test_image_unique_name(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    image.save()
    with self.assertRaises(Exception) as raised:
      image2 = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    DiskImage.objects.get(name=image.name).delete()
    self.assertEqual(IntegrityError, type(raised.exception))

  def test_image_max_length(self):
    image = create_image(self, 'a'*101, 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    data = {'name': image.name, 'devicetype': image.devicetype, 'disk_image': image.disk_image}
    form = ImageForm(data)
    self.assertFalse(form.is_valid())

class DeviceFormTest(TestCase):

  def test_valid_device_form(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': device.disk_image, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    self.assertTrue(form.is_valid())
  
  def test_device_name_max_length(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = create_device(self, 'a'*101, '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': device.disk_image, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    self.assertFalse(form.is_valid())
    
  def test_device_ram_max_length(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = create_device(self, 'test_device', '9'*9, 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': device.disk_image, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    self.assertFalse(form.is_valid())

  def test_device_token_max_length(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token'*8, 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': device.disk_image, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    self.assertFalse(form.is_valid())

  def test_device_unique_name(self):
    image = create_image(self, 'test_image', 'pc', '../ubuntu-18.04.2-live-server-amd64.iso')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    device.save()
    with self.assertRaises(Exception) as raised:
      device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    Device.objects.get(name=device.name).delete()
    self.assertEqual(IntegrityError, type(raised.exception))
from django.test import TestCase, TransactionTestCase
from django.db import IntegrityError
from django.urls import reverse
from django.core.serializers import serialize
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from .models import Device, DiskImage, EthernetPorts, EthernetCable
from .models import ImageForm, DeviceForm
import libvirt
import json
import os

# Table of contents

# 1. Models tests
# 2. Forms tests
# 3. Views tests

# Models tests

def create_image(self, name, devicetype):
  file_path = os.path.join(settings.MEDIA_ROOT, 'disk_images/TempleOS_1.ISO')
  diskimage = open(file_path, 'rb')
  return DiskImage.objects.create(name=name, devicetype=devicetype, disk_image=SimpleUploadedFile(diskimage.name, diskimage.read(), content_type='multipart/form-data'))

def create_device(self, name, ram, disk_size, cpus, cell_id, disk_image, token, console_port):
  return Device.objects.create(name=name, ram=ram, disk_size=disk_size, cpus=cpus, cell_id=cell_id, disk_image=disk_image, token=token, console_port=console_port)

def create_ethernet_ports(self, virtual_machine, mac_address):
  return EthernetPorts.objects.create(virtual_machine=virtual_machine, mac_address=mac_address)

class DiskImageTest(TestCase):

  def test_image_creation(self):
    image = create_image(self, 'test_image', 'pc')
    # copy - test the uniqueness of the name field
    self.assertTrue(isinstance(image,DiskImage))

class DeviceTest(TestCase):
  
  def test_device_creation(self):
    image = create_image(self, 'test_image', 'pc')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    self.assertTrue(isinstance(device,Device))

class EthernetPortsTest(TestCase):
    
  def test_ethernet_ports_creation(self):
    image = create_image(self, 'test_image', 'pc')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    ethernet_port = create_ethernet_ports(self, device, 'MA:CA:DD:RE:SS:XD')
    self.assertTrue(isinstance(ethernet_port, EthernetPorts))

class EthernetCableTest(TestCase):

  def create_ethernet_cable(self, name, source, target, cell_id):
    return EthernetCable.objects.create(name=name, source=source, target=target, cell_id=cell_id)

  def test_ethernet_cable(self):
    image = create_image(self, 'test_image', 'pc')
    source_device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    source = create_ethernet_ports(self, source_device, 'MA:CA:DD:RE:SS:XD')
    target_device = create_device(self, 'test_device_2', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    target = create_ethernet_ports(self, target_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = self.create_ethernet_cable('test-cable', source, target, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_source(self):
    image = create_image(self, 'test_image', 'pc')
    target_device = create_device(self, 'test_device_2', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    target = create_ethernet_ports(self, target_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = self.create_ethernet_cable('test-cable', None, target, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_target(self):
    image = create_image(self, 'test_image', 'pc')
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
    image = create_image(self, 'Ubuntu Test Image lmaoo', 'pc')
    data = {'name': image.name, 'devicetype': image.devicetype, 'disk_image': image.disk_image}
    form = ImageForm(data)
    print(form.errors)
    self.assertTrue(form.is_valid())

  def test_image_unique_name(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    with self.assertRaises(Exception) as raised:
      image2 = create_image(self, 'test_image', 'pc')
    DiskImage.objects.get(name=image.name).delete()
    self.assertEqual(IntegrityError, type(raised.exception))

  def test_image_max_length(self):
    image = create_image(self, 'a'*101, 'pc')
    data = {'name': image.name, 'devicetype': image.devicetype, 'disk_image': image.disk_image}
    form = ImageForm(data)
    self.assertFalse(form.is_valid())

class DeviceFormTest(TransactionTestCase):

  def test_valid_device_form(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    device = create_device(self, 'ubuntu_test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': image.id, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    print(form.errors)
    self.assertTrue(form.is_valid())
  
  def test_device_name_max_length(self):
    image = create_image(self, 'test_image', 'pc')
    device = create_device(self, 'a'*101, '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': device.disk_image, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    self.assertFalse(form.is_valid())
    
  def test_device_ram_max_length(self):
    image = create_image(self, 'test_image', 'pc')
    device = create_device(self, 'test_device', '9'*9, 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': device.disk_image, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    self.assertFalse(form.is_valid())

  def test_device_token_max_length(self):
    image = create_image(self, 'test_image', 'pc')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token'*8, 10015)
    data = {'name': device.name, 'ram': device.ram, 'disk_size': device.disk_size, 'cpus': device.cpus, 'cell_id': device.cell_id, 'disk_image': device.disk_image, 'token': device.token, 'console_port': device.console_port}
    form = DeviceForm(data)
    self.assertFalse(form.is_valid())

  def test_device_unique_name(self):
    image = create_image(self, 'test_image', 'pc')
    device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    device.save()
    with self.assertRaises(Exception) as raised:
      device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    Device.objects.get(name=device.name).delete()
    self.assertEqual(IntegrityError, type(raised.exception))

#No forms for Ethernet Cables - data is automatically entered by the system and so doesn't need one

# 3. Views Tests

class XmlViewTest(TestCase):

  def get_xml(self):
    xml_file = open(os.path.join(settings.STATIC_ROOT, 'graph.xml'), 'r')
    xml_string = xml_file.read()
    xml_file.close()
    return xml_string

  def test_xml_retreival(self):
    url = reverse('retrieve_xml')
    resp = self.client.get(url)
    #self.assertEqual(resp.status_code, 200)
    xml_string = self.get_xml()
    xml_dict = {'response': xml_string}
    self.assertJSONEqual(
      resp.content,
      xml_dict
    )

  def test_xml_save(self):
    xml_string = self.get_xml()
    url = reverse('save_xml')
    resp = self.client.get(
      url,
      data={'XML': xml_string},
      content_type='text/xml',
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(
      resp.content,
      {'saved': True}
    )
  
  def test_xml_wrong_request_type(self):
    xml_string = self.get_xml()
    url = reverse('save_xml')
    resp = self.client.post(
      url,
      data={'XML': xml_string},
      content_type='text/xml',
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(
      resp.content,
      {'saved': False}
    )

class ImageViewTest(TestCase):

  def test_image_retrieval(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    image2 = create_image(self, 'test_image_2', 'router',)
    image2.save()
    image3 = create_image(self, 'test_image_3', 'switch',)
    image3.save()

    image_dict = {'disk_images': json.loads(serialize('json', DiskImage.objects.all()))}

    url = reverse('get_images')
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 200)
    self.maxDiff = None
    # compare last image, take a sample etc
    self.assertJSONEqual(
      resp.content,
      image_dict
    )

  def test_image_retrieval_wrong_request(self):
    url = reverse('get_images')
    resp = self.client.post(url)
    self.assertEqual(resp.status_code, 400)
    self.maxDiff = None
    # compare last image, take a sample etc
    self.assertJSONEqual(
      resp.content,
      {'disk_images': 'None'}
    )

class DeviceViewTest(TransactionTestCase):

  def lookup_device(self, device_name):
    conn = libvirt.open('qemu:///system')
    try:
      conn.lookupByName(device_name)
      conn.close()
      return True
    except:
      conn.close()
      return False

  def cleanup_crew(self, cell_id):
    url = reverse('remove_device')
    resp = self.client.get(
      url,
      data={
        'cell_id': cell_id # Same as above test
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
  
  def create_device_libvirt(self, name, cell_id, image):
    url = reverse('post_device_form')
    resp = self.client.post(
      url,
      data={
        'name': name, #invalid data
        'ram': '2048',
        'disk_size': '25',
        'cpus': '2',
        'disk_image': image.id,
        'cell_id': cell_id
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    return resp

  def test_device_creation(self):
    image = create_image(self, 'test_image_4', 'pc')
    image.save()
    image = DiskImage.objects.get(name='test_image_4')
    resp = self.create_device_libvirt('test_device', '899', image)
    self.assertEqual(self.lookup_device('test_device'), True) # Tests to see if libvirt has created the VM
    self.cleanup_crew('899') # remove its entry from libvirt
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(
      resp.content,
      {'response': 'success'}
    )
  
  def test_device_creation_wrong_request(self):
    image = create_image(self, 'test_image_4', 'pc')
    image.save()
    url = reverse('post_device_form')
    resp = self.client.get(
      url,
      data={
        'name': 'test_device',
        'ram': '2048',
        'disk_size': '25',
        'cpus': '2',
        'disk_image': image.id,
        'cell_id': '900'
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(
      resp.content,
      {
        'response': 'error',
        'message': 'Unable to add device: Wrong HTTP request'
      }
    )
  
  def test_device_creation_invalid_data(self):
    image = create_image(self, 'test_image_4', 'pc')
    image.save()
    resp = self.create_device_libvirt('a'*101, '901', image)
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(
      resp.content,
      {
        'response': 'error',
        'message': 'Unable to add device: Data entered is not valid'
      }
    )

  def test_device_name_with_space(self):
    image = create_image(self, 'test_image_4', 'pc')
    image.save()
    resp = self.create_device_libvirt('test_device_3', '902', image)
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(
      resp.content,
      {'response': 'success'}
    )
    device = Device.objects.get(name='test_device_3')
    self.assertEqual(device.name, 'test_device_3')
    self.assertEqual(self.lookup_device('test_device_3'), True) # Tests to see if libvirt has created the VM
    self.cleanup_crew('902') # remove its entry from libvirt

  def test_device_removal(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_4', '903', image)
    url = reverse('remove_device')
    resp = self.client.get(
      url,
      data={
        'cell_id': '903' # Same as above test
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(
      resp.content,
      {'result': 'success'}
    )
    self.assertEqual(self.lookup_device('test_device_4'), False)

  def test_turn_on_devices(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_4', '903', image)
    url = reverse('change_vm_state')
    resp = self.client.get(
      url,
      data={
        'state': 'start',
        'cells': ['903']
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(
      resp.content,
      {'result': 'success'}
    )
    self.cleanup_crew('903') # remove its entry from libvirt


  def test_turn_off_devices(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_4', '903', image)
    url = reverse('change_vm_state')
    resp = self.client.get(
      url,
      data={
        'state': 'stop',
        'cells': ['903']
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(
      resp.content,
      {'result': 'success'}
    )
    self.cleanup_crew('903') # remove its entry from libvirt
  
  def test_change_vm_state_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_4', '903', image)
    url = reverse('change_vm_state')
    resp = self.client.get(
      url,
      data={
        'state': 'stop',
        'cells': ['903']
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 400)
    self.assertEqual(
      resp.content,
      {'result': 'wrong request'}
    )
    self.cleanup_crew('903') # remove its entry from libvirt

  def test_device_vnc(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_4', '903', image)
    url = reverse('get_device_vnc')
    resp = self.client.get(
      url,
      data={
        'cell_id': '903',
        'cells': ['903']
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    print(resp.content)

  def test_retrieve_device_status(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_4', '903', image)

  def test_device_status_wrong_request(self):
    print('something')

  def test_get_device_vnc_link(self):
    print('something')
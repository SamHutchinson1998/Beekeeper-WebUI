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
  file_path = os.path.join(settings.MEDIA_ROOT, 'disk_images/TempleOS.ISO')
  diskimage = open(file_path, 'rb')
  return DiskImage.objects.create(name=name, devicetype=devicetype, disk_image=SimpleUploadedFile(diskimage.name, diskimage.read(), content_type='multipart/form-data'))

def create_device(self, name, ram, disk_size, cpus, cell_id, disk_image, token, console_port):
  return Device.objects.create(name=name, ram=ram, disk_size=disk_size, cpus=cpus, cell_id=cell_id, disk_image=disk_image, token=token, console_port=console_port)

def create_ethernet_ports(self, virtual_machine, mac_address):
  return EthernetPorts.objects.create(virtual_machine=virtual_machine, mac_address=mac_address)

def create_ethernet_cable(self, name, source, target, cell_id):
  return EthernetCable.objects.create(name=name, source=source, target=target, cell_id=cell_id)

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

  def test_ethernet_cable(self):
    image = create_image(self, 'test_image', 'pc')
    source_device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    source = create_ethernet_ports(self, source_device, 'MA:CA:DD:RE:SS:XD')
    target_device = create_device(self, 'test_device_2', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    target = create_ethernet_ports(self, target_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = create_ethernet_cable(self, 'test-cable', source, target, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_source(self):
    image = create_image(self, 'test_image', 'pc')
    target_device = create_device(self, 'test_device_2', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    target = create_ethernet_ports(self, target_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = create_ethernet_cable(self, 'test-cable', None, target, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_target(self):
    image = create_image(self, 'test_image', 'pc')
    source_device = create_device(self, 'test_device', '2048', 25, 2, 15, image, 'this-is-a-made-up-token', 10015)
    source = create_ethernet_ports(self, source_device, 'MA:CA:DD:RE:SS:XD')

    ethernet_cable = create_ethernet_cable(self, 'test-cable', source, None, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

  def test_ethernet_cable_wo_source_target(self):
    ethernet_cable = create_ethernet_cable(self, 'test-cable', None, None, 15)
    self.assertTrue(isinstance(ethernet_cable, EthernetCable))

# Forms tests

class ImageFormTest(TransactionTestCase):

  def test_valid_image_form(self):
    file_path = os.path.join(settings.MEDIA_ROOT, 'disk_images/TempleOS.ISO')
    diskimage = open(file_path, 'rb')
    data = {'name': 'Ubuntu Test Image lmaoo', 'devicetype': 'pc', 'disk_image': SimpleUploadedFile(diskimage.name, diskimage.read(), content_type='multipart/form-data')}
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
    image = DiskImage.objects.get(name='test_image')
    data = {'name': 'ubuntu_test_device', 'ram': '2048', 'disk_size': 25, 'cpus': 2, 'cell_id': 15, 'disk_image': image, 'token': 'this-is-a-made-up-token', 'console_port': 10015}
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

  def test_remove_image(self):
    image = create_image(self, 'test_image_5', 'pc')
    image.save()
    url = reverse('remove_image')
    resp = self.client.post(
      url,
      data={
        'diskImages': 'test_image_5'
      }
    )
    self.assertRedirects(
      resp,
      '/',
      status_code=302,
      target_status_code=200,
      msg_prefix='',
      fetch_redirect_response=True
    )
  
  def test_remove_image_wrong_request(self):
    image = create_image(self, 'test_image_5', 'pc')
    image.save()
    url = reverse('remove_image')
    resp = self.client.get(
      url,
      data={
        'diskImages': '[test_image_5]'
      }
    )
    self.assertTrue(resp.content, {'result': 'wrong request'})

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
        'cell_id': cell_id
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
    self.create_device_libvirt('test_device_5', '903', image)
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
    self.assertEqual(self.lookup_device('test_device_5'), False)

  def test_turn_on_devices(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    url = reverse('change_vm_state')
    resp = self.client.get(
      url,
      data={
        'state': 'start',
        'cells': '[903]'
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(
      resp.content,
      {'result': 'success'}
    )
    self.cleanup_crew('903') # remove its entry from libvirt


  def test_turn_off_devices(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    url = reverse('change_vm_state')
    resp = self.client.get(
      url,
      data={
        'state': 'stop',
        'cells': '[903]'
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(
      resp.content,
      {'result': 'success'}
    )
    self.client.get(url, data={'state': 'start', 'cells': '[903]'})
    self.cleanup_crew('903') # remove its entry from libvirt

  def test_change_vm_state_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    url = reverse('change_vm_state')
    resp = self.client.post(
      url,
      data={
        'state': 'stop',
        'cells': '[903]'
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(
      resp.content,
      {'result': 'wrong request'}
    )
    self.cleanup_crew('903') # remove its entry from libvirt

  def test_device_vnc(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    url = reverse('get_device_vnc')
    resp = self.client.get(
      url,
      data={
        'cell_id': '903',
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    device = Device.objects.get(name='test_device_5')
    self.assertRedirects(
      resp,
      f'/load_device_vnc?path=websockify?token={device.token}',
      status_code=302,
      target_status_code=200,
      msg_prefix='',
      fetch_redirect_response=True
    )
    self.cleanup_crew('903') # remove its entry from libvirt

  def test_device_vnc_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    url = reverse('get_device_vnc')
    resp = self.client.post(
      url,
      data={
        'cell_id': '903',
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(
      resp.content,
      {'result': 'wrong request'}
    )
    self.cleanup_crew('903') # remove its entry from libvirt    

  def test_retrieve_device_status(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    url = reverse('get_device_status')
    resp = self.client.get(url, data={'cell_id': '903'})
    self.assertJSONEqual( resp.content, {'device_status': 'status_online'})
    self.assertEqual(resp.status_code, 200)

    # If the device has been turned off
    self.client.get(reverse('change_vm_state'), data={'state': 'stop', 'cells': '[903]'})
    resp = self.client.get(url,data={'cell_id': '903'})
    self.assertJSONEqual(resp.content, {'device_status': 'status_offline'})
    self.assertEqual(resp.status_code, 200)

    # Turn the device back on
    self.client.get(reverse('change_vm_state'), data={'state': 'start', 'cells': '[903]'})
    # if the device has been removed and there's no record of it
    self.cleanup_crew('903') # remove its entry from libvirt
    resp = self.client.get(url,data={'cell_id': '903'})

    self.assertJSONEqual(resp.content, {'device_status': 'status_unknown'})
    self.assertEqual(resp.status_code, 200)

  def test_device_status_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    url = reverse('get_device_status')
    resp = self.client.post(
      url,
      data={
        'cell_id': '903'
      }
    )
    self.assertJSONEqual( resp.content, {'result': 'wrong request'})
    self.assertEqual(resp.status_code, 400)
    self.cleanup_crew('903') # remove its entry from libvirt

  def test_get_devices(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    self.create_device_libvirt('test_device_5', '903', image)
    self.create_device_libvirt('test_device_6', '905', image)
    self.create_device_libvirt('test_device_7', '906', image)

    resp = self.client.get(reverse('get_devices'))
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(
      resp.content,
      {'devices': json.loads(serialize('json', Device.objects.all()))}
    )
    self.cleanup_crew('903')
    self.cleanup_crew('905')
    self.cleanup_crew('906')

class EthernetCableViewTest(TransactionTestCase):

  def create_ethernet_cable(self, name, cell_id):
    resp = self.client.get(
      reverse('create_network_bridge'),
      data={
        'bridge_name': name,
        'cell_id': cell_id
      }
    )
    return resp

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
  
  def cleanup_crew_device_edition(self, cell_id):
    url = reverse('remove_device')
    resp = self.client.get(
      url,
      data={
        'cell_id': cell_id
      },
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )

  def cleanup_crew(self, cell_id):
    self.client.get(reverse('destroy_network_bridge'), data={'cell_id': cell_id})

  def test_ethernet_cable_creation(self):
    # Ethernet cable creation is somewhat more automated than devices - name is auto generated
    resp = self.create_ethernet_cable('test_cable_1', '904')
    self.assertJSONEqual(resp.content, {'response': 'success'})
    self.assertEqual(resp.status_code, 200)
    self.cleanup_crew('904')

  def test_ethernet_cable_creation_wrong_request(self):
    resp = self.client.post(
      reverse('create_network_bridge'),
      data={
        'bridge_name': 'test_bridge_1',
        'cell_id': '904'
      }
    )
    self.assertJSONEqual(resp.content, {'result': 'wrong request'})
    self.assertEqual(resp.status_code, 400)

  def test_ethernet_cable_creation_error(self):
    # can bluff an error by creating a network which already exists
    self.create_ethernet_cable('test_bridge_1', '904')
    resp = self.create_ethernet_cable('test_bridge_1', '905') # This is the response we care about

    self.assertJSONEqual(resp.content, {'error': 'Failed to create an ethernet cable in the backend'})
    self.assertEqual(resp.status_code, 500)

  def test_ethernet_cable_removal(self):
    # first create a network bridge
    self.create_ethernet_cable('test_bridge_1', '904')
    # then test it's removal
    resp = self.client.get(reverse('destroy_network_bridge'), data={'cell_id': '904'})
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(resp.content, {'response': 'success'})

  def test_ethernet_cable_removal_wrong_request(self):
    self.create_ethernet_cable('test_bridge_1', '904')
    # then test it's removal
    resp = self.client.post(reverse('destroy_network_bridge'), data={'cell_id': '904'})
    self.assertJSONEqual(resp.content, {'result': 'wrong request'})
    self.assertEqual(resp.status_code, 400)
    self.cleanup_crew('904')

  def test_connect_cable(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    self.create_device_libvirt('test_device_6', '905', image)
    self.create_ethernet_cable('test_bridge_1', '904')

    # test both source and target endpoints
    url = reverse('connect_cable')
    resp = self.client.get(
      url,
      data = {'cell_id': '904','device': '903','endpoint': 'source'}
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(resp.content, {'result': 'success'})

    resp = self.client.get(
      url,
      data = {'cell_id': '904','device': '905','endpoint': 'target'}
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(resp.content, {'result': 'success'})

    self.cleanup_crew('904')
    self.cleanup_crew_device_edition('903')
    self.cleanup_crew_device_edition('905')

  def test_connect_cable_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    self.create_ethernet_cable('test_bridge_1', '904')

    # test both source and target endpoints
    url = reverse('connect_cable')
    resp = self.client.post(
      url,
      data = {'cell_id': '904','device': '903','endpoint': 'source'}
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(resp.content, {'result': 'wrong request'})
    self.cleanup_crew('904')
    self.cleanup_crew_device_edition('903')
  
  def test_disconnect_ethernet_cable(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    self.create_device_libvirt('test_device_6', '905', image)
    self.create_ethernet_cable('test_bridge_1', '904')
    # connect the cable first
    self.client.get(
      reverse('connect_cable'),
      data = {'cell_id': '904','device': '903','endpoint': 'source'}
    )
    self.client.get(
      reverse('connect_cable'),
      data = {'cell_id': '904','device': '905','endpoint': 'target'}
    )
    # test disconnect of both source and target
    resp = self.client.get(
      reverse('disconnect_cable'),
      data={'cell_id': '904', 'endpoint': 'source'}
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(resp.content, {'result': 'success'})

    resp = self.client.get(
      reverse('disconnect_cable'),
      data={'cell_id': '904', 'endpoint': 'target'}
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(resp.content, {'result': 'success'})
    self.cleanup_crew('904')
    self.cleanup_crew_device_edition('903')
    self.cleanup_crew_device_edition('905')
    
  def test_disconnect_ethernet_cable_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    self.create_ethernet_cable('test_bridge_1', '904')
    # connect the cable first
    resp = self.client.post(
      reverse('connect_cable'),
      data = {'cell_id': '904','device': '903','endpoint': 'source'}
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(resp.content, {'result': 'wrong request'})

  def test_connect_device_to_internet(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    resp = self.client.get(
      reverse('connect_device_to_internet'),
      data={'cell_id': '903'}
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(resp.content, {'result': 'success'})
    self.cleanup_crew_device_edition('903')

  def test_connect_device_to_internet_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    resp = self.client.post(
      reverse('connect_device_to_internet'),
      data={'cell_id': '903'}
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(resp.content, {'result': 'wrong request'})
    self.cleanup_crew_device_edition('903')

  def test_disconnect_device_from_internet(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    # connect it to the internet
    self.client.get(
      reverse('connect_device_to_internet'),
      data={'cell_id': '903'}
    )
    # now disconnect it from the internet
    resp = self.client.get(
      reverse('disconnect_device_from_internet'),
      data={'cell_id': '903'}
    )
    self.assertEqual(resp.status_code, 200)
    self.assertJSONEqual(resp.content, {'result': 'success'})
    self.cleanup_crew_device_edition('903')

  def test_disconnect_device_from_internet_wrong_request(self):
    image = create_image(self, 'test_image', 'pc')
    image.save()
    # create a device
    self.create_device_libvirt('test_device_5', '903', image)
    resp = self.client.post(
      reverse('disconnect_device_from_internet'),
      data={'cell_id': '903'}
    )
    self.assertEqual(resp.status_code, 400)
    self.assertJSONEqual(resp.content, {'result': 'wrong request'})
    self.cleanup_crew_device_edition('903')



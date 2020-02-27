import libvirt
import sys
from xml.dom import minidom
from .models import DiskImage, VirtualMachine
from django.conf import settings
import os

def lookup_domain(cell_id):
  conn = libvirt.open('qemu:///system')
  vm_record = VirtualMachine.objects.get(cell_id=cell_id)
  dom = conn.lookupByName(vm_record.name)
  conn.close()
  return dom

# Can still be useful for another day, maybe when a user decides to VNC into a VM? 
def get_domain_vnc_socket(domain):
  host_and_port = []
  port = 5900 # default port
  host = '127.0.0.1' # default host
  raw_xml = domain.XMLDesc(0)
  xml = minidom.parseString(raw_xml)
  graphicsTypes = xml.getElementsByTagName('graphics')
  for graphicsType in graphicsTypes:
    port = graphicsType.getAttribute('port')
    host = graphicsType.getAttribute('listen')
  host_and_port.append(host)
  host_and_port.append(port)
  return host_and_port

def create_virtual_machine(request):
  # create a .img file first then use that as the hard disk for the VM.
  # disk image goes into the cdrom compartment of the XML.
  name = request.POST.get('name',None)
  name.replace(' ', '_')# Libvirt and file dirs don't like some names with spaces in, lul
  memory = request.POST.get('ram',None)
  disk_size = request.POST.get('disk_size',None)
  cpus = request.POST.get('cpus',None)
  disk_image = DiskImage.objects.get(pk=request.POST.get('disk_image',None)).disk_image
  cell_id = request.POST.get('cell_id', None)
  # Have to make another DB call just to get the auto generated token
  token = VirtualMachine.objects.get(cell_id=cell_id).token
  
  xml = f"""
  <domain type='kvm'>
    <name>{name}</name>
    <memory unit='MB'>{memory}</memory>
    <currentmemory unit='MB'>{memory}</currentmemory>
    <vcpu placement='static'>{cpus}</vcpu>
    <clock sync='localtime'/>
    <resource>
      <partition>/machine</partition>
    </resource>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>destroy</on_crash>
    <os>
      <type arch='x86_64' machine='pc-i440fx-bionic'>hvm</type>
      <boot dev='hd'/>
      <boot dev='cdrom'/>
    </os>
    <features>
      <acpi/>
      <apic/>
    </features>
    <devices>
      <emulator>/usr/bin/kvm-spice</emulator>
      <disk type='file' device='disk'>
        <source file='/var/lib/libvirt/images/{name}.img'/>
        <backingstore/>
        <driver name='qemu' type='raw'/>
        <target dev='vda' bus='virtio'/>
      </disk>
      <disk type='file' device='cdrom'>
        <driver name='qemu' type='raw'/>
        <source file='{settings.MEDIA_ROOT}/{disk_image}'/>
        <backingstore/>
        <target dev='hda' bus='ide'/>
        <readonly/>
      </disk>
      <input type='mouse' bus='ps2'/>
      <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'/>
    </devices>
  </domain>"""
  #print(xml)
  spawn_machine(disk_size, name, xml, token)

def spawn_machine(disk_size, name, xml, token):
  config = xml
  conn = libvirt.open('qemu:///system')
  dom = conn.defineXML(config)
  if dom == None:
    print('Failed to define a domain from an XML definition.', file=sys.stderr)
  else:
    os.system(f'qemu-img create -f raw /var/lib/libvirt/images/{name}.img {disk_size}G')
    if dom.create() < 0:
      print('Can not boot guest domain.', file=sys.stderr)
    else:
      print('Guest '+dom.name()+' has booted', file=sys.stderr)
      socket = get_domain_vnc_socket(dom)
      create_device_token(socket, token)
  conn.close()

def create_device_token(socket, token):
  token_mapping = "{}: {}:{}".format(token, socket[0], socket[1])
  token_filepath = os.path.join(settings.BASE_DIR, f'beekeeper_webui/assets/javascript/novnc/vnc_tokens/{token}.ini')
  token_file = open(token_filepath, 'w')
  token_file.write(token_mapping)
  token_file.close

def remove_machine(virtual_machine):
  conn = libvirt.open('qemu:///system')
  dom = conn.lookupByName(virtual_machine.name)
  dom.undefine()
  dom.destroy()
  print(f'domain {virtual_machine.name} destroyed')

  # remove img associated with the VM
  os.system(f'rm -rf /var/lib/libvirt/images/{virtual_machine.name}.img')

  # remove the VNC token too
  token_filepath = os.path.join(settings.BASE_DIR, f'beekeeper_webui/assets/javascript/novnc/vnc_tokens/{virtual_machine.token}.ini')
  os.remove(token_filepath)

def turn_off_devices(devices):
  conn = libvirt.open('qemu:///system')
  if len(devices) == 0:
    # shut off all devices
    domains = conn.listAllDomains(0)
    for domain in domains:
      if domain.isActive(): # If device is not already turned off
        domain.destroy()
  else:
    #shut off selected devices
    for device in devices:
      vm_name = VirtualMachine.objects.get(cell_id=device).name
      dom = conn.lookupByName(vm_name)
      if dom.isActive(): # If device is not already turned off
        dom.destroy()
  conn.close()

def turn_on_devices(devices):
  conn = libvirt.open('qemu:///system')
  if len(devices) == 0:
    # turn on all devices
    domains = conn.listAllDomains(0)
    for domain in domains:
      if domain.isActive() < 1: # If device is already turned on
        domain.create()
  else:
    #turn on selected devices
    for device in devices:
      vm_name = VirtualMachine.objects.get(cell_id=device).name
      dom = conn.lookupByName(vm_name)
      if dom.isActive() < 1: # If device is already turned on
        dom.create()
  conn.close()

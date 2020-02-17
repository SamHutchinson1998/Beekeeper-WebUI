import libvirt
import sys
from xml.dom import minidom
from .models import DiskImage
from django.conf import settings
import os


def get_domains():
  domain_list = []
  conn = libvirt.open('qemu:///system')
  domains = conn.listAllDomains(0)
  for domain in domains:
    domain_list.append(domain.name())
    port = get_domain_port(domain)
    domain_list.append(port)
  conn.close()
  return domain_list

# Can still be useful for another day, maybe when a user decides to VNC into a VM? 
def get_domain_port(domain):
  port = 5900 #first port a domain attaches to if there are no other domains
  raw_xml = domain.XMLDesc(0)
  xml = minidom.parseString(raw_xml)
  graphicsTypes = xml.getElementsByTagName('graphics')
  for graphicsType in graphicsTypes:
    port = graphicsType.getAttribute('port')
  return port

def create_virtual_machine(request):
  # create a .img file first then use that as the hard disk for the VM.
  # disk image goes into the cdrom compartment of the XML.
  name = request.POST.get('name',None)
  memory = request.POST.get('ram',None)
  disk_size = request.POST.get('disk_size',None)
  cpus = request.POST.get('cpus',None)
  disk_image = DiskImage.objects.get(pk=request.POST.get('disk_image',None)).disk_image
  
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
  spawn_machine(disk_size, name, xml)

def spawn_machine(disk_size, name, xml):
  config = xml
  # Plan B is to use a shellscript to do it haha xd
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
  conn.close()

def remove_machine(virtual_machine):
  conn = libvirt.open('qemu:///system')
  dom = conn.lookupByName(virtual_machine.name)
  dom.undefine()
  dom.destroy()
  print(f'domain {virtual_machine.name} destroyed')
  os.system(f'rm -rf /var/lib/libvirt/images/{virtual_machine.name}.img')

def turn_off_devices():
  print('devices turned off')

def turn_on_devices():
  print('devices turned on')
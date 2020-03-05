from django.http import JsonResponse
from xml.dom import minidom
from .models import DiskImage, VirtualMachine, EthernetPorts
from django.conf import settings
import os
import uuid
import libvirt
import sys

def lookup_domain(cell_id):
  dom = None
  conn = libvirt.open('qemu:///system')
  try:
    vm_record = VirtualMachine.objects.get(cell_id=cell_id)
    dom = conn.lookupByName(vm_record.name)
  except:
    dom = None
  finally:
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

def create_virtual_machine(cell_id):
  # create a .img file first then use that as the hard disk for the VM.
  # disk image goes into the cdrom compartment of the XML.
  # x.ethernetports_set.all()

  # token generation happens here
  token = str(uuid.uuid4())
  vm = VirtualMachine.objects.get(cell_id=cell_id)
  vm.token = token
  vm.save()

  name = vm.name
  memory = vm.ram
  disk_size = vm.disk_size
  cpus = vm.cpus
  disk_image = vm.disk_image.disk_image

  ethernet_ports = """"""
  for port in vm.ethernetports_set.all():
    xml = """
    <interface></interface>\n
    """
    ethernet_ports += xml

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
      {ethernet_ports}
      <disk type='file' device='disk'>
        <source file='/var/lib/libvirt/images/{name}.qcow2'/>
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
      <input type='keyboard' bus='ps2'/>
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
    os.system(f'qemu-img create -f raw /var/lib/libvirt/images/{name}.qcow2 {disk_size}G')
    if dom.create() < 0:
      print('Can not boot guest domain.', file=sys.stderr)
    else:
      print('Guest '+dom.name()+' has booted', file=sys.stderr)
      socket = get_domain_vnc_socket(dom)
      create_device_token(socket, token)
  conn.close()

def create_ethernet_ports(cell_id, ethernet_ports):
  vm = VirtualMachine.objects.get(cell_id=cell_id)
  for port in range(ethernet_ports):
    ethernet_port = EthernetPorts(virtual_machine=vm)
    ethernet_port.save()
  return True

def generate_error_message(message, cell_id):
  try:
    vm = VirtualMachine.objects.get(cell_id=cell_id)
    remove_machine(vm)
  finally:
    return JsonResponse({'response':'error', 'message': message}, status=200)

def create_device_token(socket, token):
  token_mapping = "{}: {}:{}".format(token, socket[0], socket[1])
  token_filepath = os.path.join(settings.BASE_DIR, f'assets/javascript/novnc/vnc_tokens/{token}.ini')
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
  os.system(f'rm -rf /var/lib/libvirt/images/{virtual_machine.name}.qcow2')

  # remove the VNC token too
  token_filepath = os.path.join(settings.BASE_DIR, f'assets/javascript/novnc/vnc_tokens/{virtual_machine.token}.ini')
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

def create_device_req(request):
  if request.method == 'POST':
    update_request = request.POST.copy()
    name = update_request['name'].replace(" ", '_') # ensure spaces in the name are replaced with underscores
    update_request.update({'name':name})
    return update_request

def get_vm_status(cell_id):
  vm = lookup_domain(cell_id)
  if vm is None:
    return 'status_unknown'
  else:
    if vm.isActive():
      return 'status_online'
    if vm.isActive() < 1:
      return 'status_offline'

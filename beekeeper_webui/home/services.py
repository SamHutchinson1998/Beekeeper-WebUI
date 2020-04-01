from django.http import JsonResponse
from .models import DiskImage, VirtualMachine, EthernetPorts
from django.conf import settings
from xml.dom import minidom
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


  # Here I was experimenting with adding ethernet ports to a device manually

  #ethernet_ports = """ """
  #for port in vm.ethernetports_set.all():
    #xml = """
    #<interface>

    #</interface>\n
    #"""
    #ethernet_ports += xml

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
      <serial type='pty'>
        <target port='0'/>
      </serial>
      <console type='pty'>
        <target type='serial' port='0'/>
      </console>
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
      dom.setAutostart(1)
      print('Guest '+dom.name()+' has booted', file=sys.stderr)
      socket = get_domain_vnc_socket(dom)
      create_device_token(socket, token)
  conn.close()

def create_ethernet_ports(cell_id, ethernet_ports):
  vm = VirtualMachine.objects.get(cell_id=cell_id)
  i = 0
  for port in range(ethernet_ports):
    ethernet_port = EthernetPorts(virtual_machine=vm,port_no=i)
    ethernet_port.save()
    i += 1
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

def create_network(name):
  xml = f""" 
  <network>
    <name>{name}</name>
    <bridge name="{name}" stp='off' macTableManager="libvirt"/> 
    <mtu size="9216"/> 
  </network>
  """
  conn = libvirt.open('qemu:///system')
  if conn == None:
    conn.close()
    return 'Failed to open connection to QEMU'
  network = conn.networkDefineXML(xml)
  if network == None:
    conn.close()
    return 'Failed to create an ethernet cable in the backend'
  network.setAutostart(1) # Sets the network to autostart upon bootup of libvirt
  #network.create()
  conn.close()
  return 'success'

def destroy_network(name):
  conn = libvirt.open('qemu:///system')
  if conn == None:
    conn.close()
    return 'Failed to open connection to QEMU'
  network = conn.networkLookupByName(name)
  network.destroy()
  network.undefine()
  conn.close()
  return 'success'

def plug_cable_in_devices(name, device_one_ethernet, device_two_ethernet):
  # Needs more work!
  eth_one = EthernetPorts.objects.get(id=device_one_ethernet)
  eth_two = EthernetPorts.objects.get(id=device_two_ethernet)
  device_one_record = eth_one.virtual_machine
  device_two_record = eth_two.virtual_machine
  if plug_cable_in_device(eth_one, device_one_record, name):
    if plug_cable_in_device(eth_two, device_two_record, name):
      return 'success'
    else:
      return f'Unable to plug ethernet cable to {device_two_record.name}'
  else:
    return f'Unable to plug ethernet cable to {device_one_record.name}'

def plug_cable_in_device(eth, device, name):
  conn = libvirt.open('qemu:///system')
  if conn == None:
    conn.close()
    return False
  dom = conn.lookupByName(device.name)
  #device_xml = get_device_xml_from_domain(dom)
  new_xml = return_int_xml_from_domain(name, eth, dom)
  if new_xml:
    dom.updateDeviceFlags(new_xml)
    #if dom.updateDeviceFlags(new_xml): # If updating the device XML was successful
      #conn.close()
      #return True
    #else:
      #conn.close()
      #return False
  else:
    return False
  
def get_device_xml_from_domain(dom):
  raw_xml = dom.XMLDesc(0)
  dom_xml = minidom.parseString(raw_xml)
  devices = dom_xml.getElementsByTagName('devices')
  return devices

def return_int_xml_from_domain(name, eth, dom):
  raw_xml = dom.XMLDesc(0)
  dom_xml = minidom.parseString(raw_xml)
  new_xml = minidom.parseString(f"""
  <interface type='bridge'>
    <source bridge='{name}'/>
    <model type='virtio'/>
  </interface>
  """)
  eth_port = int(eth.port_no)
  count = 0
  for interface in dom_xml.getElementsByTagName('interface'):
    if eth_port == count: # if the target ethernet port is found
      interface = new_xml
      print(dom_xml.toxml().replace('<?xml version="1.0" ?>', ''))
      return dom_xml.toxml()
    else:
      count += 1
  return False

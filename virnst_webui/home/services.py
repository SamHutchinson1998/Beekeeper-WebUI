import libvirt
from xml.dom import minidom

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

def get_domain_port(domain):
  port = 5900 #first port a domain attaches to if there are no other domains
  raw_xml = domain.XMLDesc(0)
  xml = minidom.parseString(raw_xml)
  graphicsTypes = xml.getElementsByTagName('graphics')
  for graphicsType in graphicsTypes:
    port = graphicsType.getAttribute('port')
  return port

def get_image_vector(device):
  # Get the vector graphic associated with the image
  switcher = {
    'ROUTER': '../static/devices/router.svg',
    'SWITCH': '../static/devices/switch.svg',
    'SERVER': '../static/devices/server.svg'
  }
  # Return the graphic for computer by default if the device isn't found
  return switcher.get(device, '../static/devices/computer.svg')
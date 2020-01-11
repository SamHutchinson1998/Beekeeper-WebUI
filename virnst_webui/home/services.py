import libvirt

def get_domains():
  conn = libvirt.open('qemu:///system')
  domains = conn.listAllDomains(0)
  conn.close()
  return domains

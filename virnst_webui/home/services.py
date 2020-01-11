import libvirt

def get_domains():
  domain_list = []
  conn = libvirt.open('qemu:///system')
  domains = conn.listAllDomains(0)
  for domain in domains:
    domain_list.append(domain.name())
  conn.close()
  return domain_list

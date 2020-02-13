# Example-6.py
from __future__ import print_function
import sys
import libvirt
from xml.dom import minidom

conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)

domains = conn.listAllDomains(0)
if len(domains) != 0:
    for domain in domains:
        print(domain.name())
	raw_xml = domain.XMLDesc(0)
	xml = minidom.parseString(raw_xml)
	graphicsTypes = xml.getElementsByTagName('graphics')
	for graphicsType in graphicsTypes:
	    print(graphicsType.getAttribute('port'))
else:
    print('  None')

conn.close()
exit(0)

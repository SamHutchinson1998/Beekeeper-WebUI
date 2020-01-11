#! bin/bash
# install script
# needs to be ran with root permissions

apt-install python-pip
apt-get install libvirt-dev
pip install libvirt-python

apt-get install python3-venv
python3 -m venv venv
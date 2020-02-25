#! bin/bash
# install script
# needs to be ran with root permissions

apt install python3-venv python3-dev python3-setuptools python3-pip nginx curl libpq-dev

apt-get install libvirt-dev

echo "alias python=python3" >> .bashrc

cp /settings/gunicorn.service /etc/systemd/system/gunicorn.service
cp /settings/gunicorn.socket /etc/systemd/system/gunicorn.socket

pip install libvirt-python
pip install gunicorn

systemctl start gunicorn.socket
systemctl enable gunicorn.socket

cd
apt install cpu-checker
apt update
apt install qemu qemu-kvm libvirt-bin bridge-utils virt-manager
apt install npm
npm install mxgraph
EXPORT "vnc_listen = 0.0.0.0" >> /etc/libvirt/qemu.conf
chown -R $USER /var/lib/libvirt/images

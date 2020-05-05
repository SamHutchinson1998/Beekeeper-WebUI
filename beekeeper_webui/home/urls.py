from django.urls import path
from .views import HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('home', HomePageView.saveXml, name='save_xml'),
    path('retrieveXml', HomePageView.retrieveXml, name='retrieve_xml'),
    path('upload_image', HomePageView.upload_images, name='upload_image'),
    path('get_images',HomePageView.get_images, name='get_images'),
    path('post_device_form', HomePageView.create_device, name='post_device_form'),
    path('remove_device', HomePageView.remove_device, name='remove_device'),
    path('change_vm_state', HomePageView.change_vm_state, name='change_vm_state'),
    path('get_device_vnc', HomePageView.get_device_vnc, name='get_device_vnc'),
    path('load_device_vnc', HomePageView.load_device_vnc, name='load_device_vnc'),
    path('get_device_status', HomePageView.get_device_status, name='get_device_status'),
    path('reload_body', HomePageView.reload_body, name="reload_body"),
    path('remove_image', HomePageView.remove_image, name="remove_image"),
    path('create_network_bridge', HomePageView.create_network_bridge, name="create_network_bridge"),
    path('destroy_network_bridge', HomePageView.destroy_network_bridge, name="destroy_network_bridge"),
    path('get_ethernet_ports', HomePageView.get_ethernet_ports, name="get_ethernet_ports"),
    path('get_devices', HomePageView.get_devices, name="get_devices"),
    path('connect_cable', HomePageView.connect_cable, name="connect_cable"),
    path('disconnect_cable', HomePageView.disconnect_cable, name='disconnect_cable'),
    path('lookup_device', HomePageView.lookup_device, name='lookup_device'),
    path('connect_device_to_internet', HomePageView.connect_device_to_internet, name="connect_device_to_internet"),
    path('disconnect_device_from_internet', HomePageView.disconnect_device_from_internet, name="disconnect_device_from_internet"),
    path('get_started_guide', HomePageView.get_started_guide, name='get_started_guide'),
]
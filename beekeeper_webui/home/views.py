from django.contrib import messages
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.serializers import serialize
from django.conf import settings
from django.urls import reverse
from django.template import Context, Template
from .services import destroy_network, create_network, create_ethernet_ports, generate_error_message, get_vm_status, create_device_req, lookup_domain, get_domain_vnc_socket, create_virtual_machine, remove_machine, turn_off_devices, turn_on_devices
from .models import EthernetPorts, EthernetPortsForm, ImageForm, DiskImage, VirtualMachine, VirtualMachineForm
from urllib.parse import urlencode
import os
import json

# Create your views here.

class HomePageView(TemplateView):
  template_name = 'home.html'

  def get_context_data( *args, **kwargs):
    context = {
      'form': ImageForm(),
      'device_form': VirtualMachineForm(),
      'disk_images': DiskImage.objects.all(),
      'devices': serialize('json', VirtualMachine.objects.all())
    }
    return context

  def upload_images(request):
    next = request.POST.get('next', '/')
    if request.method == "POST":
      form = ImageForm(request.POST, request.FILES)
      if form.is_valid():
        if form.save():
          messages.success(request, 'Disk Image uploaded successfully', extra_tags='alert-success')
        else:
          messages.error(request, 'Unable to save Disk Image 3', extra_tags='alert-danger')
      else:
        messages.error(request, 'Unable to save Disk Image 1', extra_tags='alert-danger')
      return HttpResponseRedirect(next)
    else:
      messages.error(request, 'Unable to save Disk Image 2', extra_tags='alert-danger')
      return HttpResponseRedirect(next)

  def retrieveXml(request):
    if request.is_ajax and request.method == "GET":
      xml_file_path = os.path.join(settings.STATIC_ROOT, 'graph.xml')
      xml_file = open(xml_file_path, 'r')
      xml_string = xml_file.read()
      xml_file.close()
      return JsonResponse({"response":xml_string}, status = 200)

  def saveXml(request):
    if request.is_ajax and request.method == "GET":
      xml_string = request.GET.get("XML", None)
      xml_file_path = os.path.join(settings.STATIC_ROOT, 'graph.xml')
      xml_file = open(xml_file_path, 'w')
      xml_file.write(xml_string)
      xml_file.close()
      return JsonResponse({"saved":True}, status = 200)
    return JsonResponse({"saved":False}, status = 200)

  def get_devices(request):
    if request.is_ajax and request.method == "GET":
      disk_images = json.loads(serialize('json', DiskImage.objects.all()))
      return JsonResponse({"disk_images":disk_images}, status = 200)

  def create_device(request):
    if request.method == "POST":
      modified_request = create_device_req(request)
      cell_id = modified_request.get('cell_id', None)
      form = VirtualMachineForm(modified_request)
      print(modified_request)
      if form.is_valid():
        if form.save():
          ethernet_ports = int(modified_request.get('ethernetports', None))
          if create_ethernet_ports(cell_id, ethernet_ports):
            create_virtual_machine(cell_id)
            return JsonResponse({'response':'success'}, status=200)
          else:
            return generate_error_message('Unable to create ethernet ports for device', cell_id)
        else:
          return generate_error_message('Unable to add device: Unable to save Device in the database', cell_id)
      else:
        return generate_error_message('Unable to add device: Data entered is not valid', cell_id)
    else:
      return generate_error_message('Unable to add device: Wrong HTTP request', None)

  def remove_device(request):
    if request.is_ajax and request.method == "GET":
      retrieved_cell_id = json.loads(request.GET.get('cell_id',None))
      vm_record = VirtualMachine.objects.get(cell_id=retrieved_cell_id)
      if vm_record.delete():
        remove_machine(vm_record)
        return JsonResponse({'result': 'success'},status = 200)
      else:
        return JsonResponse({'result': f'Unable to remove device {vm_record.name} from the database at this time'},status = 500)
  
  def change_vm_state(request):
    if request.is_ajax and request.method == "GET":
      device_list = json.loads(request.GET.get('cells', None))
      if request.GET.get('state',None) == 'start':
        turn_on_devices(device_list)
      else:
        turn_off_devices(device_list)
    return JsonResponse({},status=200)

  def get_device_vnc(request):
    cell_id = request.GET.get('cell_id', None)
    token = VirtualMachine.objects.get(cell_id=cell_id).token
    base_url = reverse('load_device_vnc')
    path = urlencode({'path':'websockify'})
    token = urlencode({'token':token})
    url = '{}?{}?{}'.format(base_url,path,token)
    return HttpResponseRedirect(url)

  def load_device_vnc(request):
    return render(request, 'vnc.html')

  def get_device_status(request):
    cell_id = request.GET.get('cell_id',None)
    device_status = get_vm_status(cell_id)
    return JsonResponse({'device_status':device_status},status=200)

  def reload_body(request):
    if request.method == 'GET':
      context = {
        'form': ImageForm(),
        'device_form': VirtualMachineForm()
      }
      return render(request, '_body.html', context)
    return JsonResponse({},status=200)

  def remove_image(request):
    next = request.POST.get('next', '/')
    if request.method == 'POST':
      images = request.POST.getlist('diskImages', None)
      for image in images:
        disk_image = DiskImage.objects.get(name=image)
        disk_image.disk_image.delete()
        disk_image.delete()
      return HttpResponseRedirect(next)

  def create_network_bridge(request):
    name = request.GET.get('bridge_name', None)
    if request.method == "GET":
      network = create_network(name)
      if network == 'success': # if network creation was not successful
        return JsonResponse({'response': network})
      else:
        return JsonResponse({'error': network})
      
  def destroy_network_bridge(request):
    name = request.GET.get('bridge_name', None)
    if request.method == "GET":
      remove_network = destroy_network(name)
      if remove_network == 'success':
        return JsonResponse({'response': remove_network})
      else:
        return JsonResponse({'error': remove_network})

  def get_ethernet_ports(request):
    cell_id = request.GET.get('cell_id', None)
    if request.method == 'GET':
      vm = VirtualMachine.objects.get(cell_id=cell_id)
      ethernet_ports = json.loads(serialize('json', vm.ethernetports_set.all()))
      return JsonResponse({'ethernet_ports': ethernet_ports})
    return JsonResponse({'error':'error'})

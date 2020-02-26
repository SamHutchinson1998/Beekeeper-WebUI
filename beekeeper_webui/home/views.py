from django.contrib import messages
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.serializers import serialize
from django.conf import settings
from django.urls import reverse
from .services import lookup_domain, get_domain_vnc_socket, create_virtual_machine, remove_machine, turn_off_devices, turn_on_devices
from .models import ImageForm, DiskImage, VirtualMachine, VirtualMachineForm
from urllib.parse import urlencode
import os
import json

# Create your views here.

class HomePageView(TemplateView):
  template_name = 'home.html'

  def get_context_data(self, *args, **kwargs):
    context = {
      'form': ImageForm(),
      'device_form': VirtualMachineForm()
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
      #xml_file = open(settings.GRAPH_FILE, "r")
      xml_file = open(xml_file_path, 'r')
      xml_string = xml_file.read()
      xml_file.close()
      return JsonResponse({"response":xml_string}, status = 200)

  def saveXml(request):
    if request.is_ajax and request.method == "GET":
      xml_string = request.GET.get("XML", None)
      xml_file_path = os.path.join(settings.STATIC_ROOT, 'graph.xml')
      #xml_file = open("graph.xml", "w")
      xml_file = open(xml_file_path, 'w')
      xml_file.write(xml_string)
      xml_file.close()
      return JsonResponse({"valid":True}, status = 200)
    return JsonResponse({"valid":False}, status = 200)

  def get_devices(request):
    if request.is_ajax and request.method == "GET":
      print(request)
      disk_images = json.loads(serialize('json', DiskImage.objects.all()))
      return JsonResponse({"disk_images":disk_images}, status = 200)
 
  def post_device_form(request):
    next = request.POST.get('next', '/')
    if request.method == "POST":
      form = VirtualMachineForm(request.POST)
      if form.is_valid():
        if form.save():
          create_virtual_machine(request)
          messages.success(request, 'Successfully added device', extra_tags='alert-success')
        else:
          messages.error(request, 'Unable to add device', extra_tags='alert-danger')
      else:
        messages.error(request, "Unable to add device", extra_tags='alert-danger')
    else:
      messages.error(request, 'Unable to add device', extra_tags='alert-danger')
    return HttpResponseRedirect(next)

  def remove_device(request):
    if request.is_ajax and request.method == "GET":
      retrieved_cell_id = json.loads(request.GET.get('cell_id',None))
      vm_record = VirtualMachine.objects.get(cell_id=retrieved_cell_id)
      if vm_record.delete():
        remove_machine(vm_record)
        return JsonResponse({'result': 'success'},status = 200)
      else:
        return JsonResponse({'result': 'error'},status = 500)
  
  def change_vm_state(request):
    if request.is_ajax and request.method == "GET":
      device_list = json.loads(request.GET.get('cells', None))
      if request.GET.get('state',None) == 'start':
        turn_on_devices(device_list)
      else:
        turn_off_devices(device_list)
    return JsonResponse({},status=200)

  def get_device_vnc(request):
    # Use this method here to get the VM object associated with the cell ID, then get VNC port and host off libvirt and then add it to the query string
    base_url = reverse('load_device_vnc')
    cell_id = request.GET.get('cell_id',None)
    domain = lookup_domain(cell_id)
    domain_vnc_socket = get_domain_vnc_socket(domain)
    query_string = urlencode({'host':domain_vnc_socket[0],'port':domain_vnc_socket[1]})
    url = '{}?{}'.format(base_url, query_string)
    return HttpResponseRedirect(url)

  def load_device_vnc(request):
    host = request.GET.get('host', None)
    port = request.GET.get('port', None)
    return render(request, 'vnc.html')

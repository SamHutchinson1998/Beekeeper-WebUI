from django.contrib import messages
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.serializers import serialize
from .services import get_domains
from .models import ImageForm, DiskImage
import json
# Create your views here.

class HomePageView(TemplateView):
  template_name = 'home.html'

  def get_context_data(self, *args, **kwargs):
    context = {
      'domains' : get_domains(),
      'form': ImageForm()
    }
    return context

  def upload_images(request):
    if request.method == "POST":
      next = request.POST.get('next', '/')
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

  def saveXml(request):
    if request.is_ajax and request.method == "GET":
      xml_string = request.GET.get("XML", None)
      print(xml_string)
      xml_file = open("graph.xml", "w")
      xml_file.write(xml_string)
      xml_file.close()
      return JsonResponse({"valid":True}, status = 200)
    return JsonResponse({"valid":False}, status = 200)
  
  def retrieveXml(request):
    if request.is_ajax and request.method == "GET":
      xml_file = open("graph.xml", "r")
      xml_string = xml_file.read()
      xml_file.close()
      return JsonResponse({"response":xml_string}, status = 200)
  
  def get_devices(request):
    if request.is_ajax and request.method == "GET":
      print(request)
      disk_images = json.loads(serialize('json', DiskImage.objects.all()))
      return JsonResponse({"disk_images":disk_images}, status = 200)

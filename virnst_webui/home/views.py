from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from .services import get_domains
from .models import ImageForm
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
    print("It works")

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


from django.shortcuts import render
from django.views.generic import TemplateView
from .services import get_domains
# Create your views here.

class HomePageView(TemplateView):
  template_name = 'home.html'
  def get_context_data(self, *args, **kwargs):
    context = {
      'domains' : get_domains(),
    }
    return context
  def saveXml(request):
    

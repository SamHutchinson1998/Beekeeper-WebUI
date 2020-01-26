from django.urls import path
from .views import HomePageView
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('home', HomePageView.saveXml, name='save_xml'),
    path('retrieveXml', HomePageView.retrieveXml, name='retrieve_xml'),
]

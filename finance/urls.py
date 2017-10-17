from django.conf.urls import url
from . import views
from django.views.generic import ListView,DetailView



urlpatterns = [
    
       # url(r'^stock/$', views.main, name = 'home_page_plot'),
       url(r'^$', views.home, name = 'home_page'),
       # url(r'^api/get_drugs/', views.get_stocks, name='get_stocks'),
       
       ]
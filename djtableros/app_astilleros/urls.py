from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('informegerencial', views.informegerencial, name='informegerencial'),
    path('cxcastilleros', views.cxcastilleros, name='cxcastilleros'),
    path('cxcastilleros_pdf', views.cxcastilleros_pdf, name='cxcastilleros_pdf')
]
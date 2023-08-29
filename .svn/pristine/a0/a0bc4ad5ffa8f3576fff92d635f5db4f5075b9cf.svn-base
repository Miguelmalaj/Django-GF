from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ventaservicio', views.ventaservicio, name='ventaservicio'),
    path('ordenesproceso', views.ordenesproceso, name='ordenesproceso'),
    path('ventarefacciones', views.ventarefacciones, name='ventarefacciones'),
    path('detalleordenes/<str:empresa>/<str:tipo_orden>/<int:year>/<int:mes>/<int:tipoconsulta>', views.detalle_ordenes, name='detalleordenes'),
]
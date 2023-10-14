from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cuentasxcobrar/', views.cuentasxcobrar, name='cuentasxcobrar'),
    path('cuentasxcobrar/pdf/', views.generatepdf_cuentasxcobrar, name='pdf_cuentasxcobrar'),
    path('cuentasxcobrar_detalle/<str:empresa>/<str:sucursal>', views.cuentasxcobrar_detalle, name='cuentasxcobrar_detalle'),
    path('cuentasxcobrar_detalle/pdf/<str:empresa>/<str:sucursal>', views.cuentasxcobrarpdf_detalle, name='cuentasxcobrarpdf_detalle'),
    path('cuentasxpagar', views.cuentasxpagar, name='cuentasxpagar'),
    path('cuentasxpagar_detalle/<str:empresa>/<str:sucursal>', views.cuentasxpagar_detalle, name='cuentasxpagar_detalle'),
]
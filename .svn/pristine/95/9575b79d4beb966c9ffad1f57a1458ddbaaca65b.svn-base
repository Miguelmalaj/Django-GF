from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('base/', views.base, name='base'),
    path('logout/', views.logout_view, name='logout'),
    path('funnelventas/', views.funnel_chart, name='funnelventas'),
    path('funnelvendedor/', views.funel_vendedor, name='funnelvendedor'),
    path('ventasanuales/', views.ventasanuales, name='ventasanuales'),
    path('entregasanuales/', views.entregasanuales, name='entregasanuales'),
    path('ventasvehiculos/', views.ventasvehiculos, name='ventasvehiculos'),
    path('ventasvehiculos_detalle/<str:bytAgencia>/<str:bytSucursal>/<str:fechareporte>', views.ventasvehiculos_detalle, name='ventasvehiculos_detalle'),
    path('resumeninvveh/', views.resumeninvveh, name='resumeninvveh'),
    path('inventario_detalle/<str:empresa>/<str:sucursal>', views.inventariovehiculos_detalle, name='inventario_detalle'),
    path('inventariovehiculos/', views.inventarioveh, name='inventariovehiculos'),
    path('planpisopagado/', views.planpisopagado, name='planpisopagado')
]
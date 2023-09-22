from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cuentasxcobrar/', views.cuentasxcobrar, name='cuentasxcobrar'),
    path('cuentasxcobrar_detalle/<str:empresa>/<str:sucursal>', views.cuentasxcobrar_detalle, name='cuentasxcobrar_detalle'),
    path('cuentasxpagar', views.cuentasxpagar, name='cuentasxpagar'),
    path('cuentasxpagar_detalle/<str:empresa>/<str:sucursal>', views.cuentasxpagar_detalle, name='cuentasxpagar_detalle'),
]
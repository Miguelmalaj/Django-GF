from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cuentasxcobrar/', views.cuentasxcobrar, name='cuentasxcobrar'),
    path('cuentasxcobrar/pdf/', views.cuentasxcobrarpdf, name='cuentasxcobrarpdf'),
    path('cuentasxcobrar_detalle/<str:empresa>/<str:sucursal>', views.cuentasxcobrar_detalle, name='cuentasxcobrar_detalle'),
    path('cuentasxcobrar_detalle/pdf/<str:empresa>/<str:sucursal>', views.cuentasxcobrarpdf_detalle, name='cuentasxcobrarpdf_detalle'),
    path('cuentasxpagar', views.cuentasxpagar, name='cuentasxpagar'),
    path('cuentasxpagar/pdf/', views.cuentasxpagarpdf, name='cuentasxpagarpdf'),
    path('cuentasxpagar_detalle/<str:empresa>/<str:sucursal>', views.cuentasxpagar_detalle, name='cuentasxpagar_detalle'),
    path('cuentasxpagar_detalle/pdf/<str:empresa>/<str:sucursal>', views.cuentasxpagarpdf_detalle, name='cuentasxpagarpdf_detalle'),
]
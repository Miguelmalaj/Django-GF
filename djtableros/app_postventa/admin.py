from django.contrib import admin
from app_postventa.models import  OpcionMenu, Permisos, Objetivos
#Register your models here.


@admin.register(OpcionMenu)
class OpcionMenu_admin(admin.ModelAdmin):
    list_display = ('nombre', 'vista', 'icono', 'orden')


@admin.register(Permisos)
class Permisos(admin.ModelAdmin):
    list_display = ('nombre', 'lista_opciones_menu', 'opcion_default')  # Agregar los métodos personalizados aquí    
    search_fields = ('nombre',)
    
    def lista_opciones_menu(self, obj):
        return ", ".join([opcion.nombre for opcion in obj.opciones_menu.all()])
    lista_opciones_menu.short_description = 'Opciones de Menú vta'  # Nombre de la columna en la vista de lista


@admin.register(Objetivos)
class ObjetivoAdmin(admin.ModelAdmin):
    list_display = ('empresa_sucursal', 'periodo', 'venta_refacciones', 'utilidad_refacciones', 'venta_servicio', 'utilidad_servicio')
    list_filter = ('empresa_sucursal', 'periodo')
    search_fields = ('empresa_sucursal', 'periodo')
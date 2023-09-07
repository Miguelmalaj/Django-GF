from django.contrib import admin
from app_postventa.models import  OpcionMenu, Permisos
# Register your models here.


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


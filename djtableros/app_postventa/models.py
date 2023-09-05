from django.db import models
from django.contrib.auth.models import Permission

# # Create your models here.
# class empresas(models.Model):
#     empresa = models.PositiveBigIntegerField()
#     sucursal = models.PositiveBigIntegerField(default=1) 
#     nombre_empresa = models.CharField(max_length=30)
#     direccion_ip = models.CharField(max_length=100)
#     usuario = models.CharField(max_length=100)
#     clave_acceso = models.CharField(max_length=100)
#     ref_cartera = models.CharField(max_length=30, default='*')
#     logo = models.CharField(max_length=100, default='')
#     bg_color = models.CharField(max_length=50, default='')

#     def __str__(self):
#         return self.nombre_empresa
    
class OpcionMenu(models.Model):
    nombre = models.CharField(max_length=50)
    vista = models.CharField(max_length=100)  # Nombre de la vista
    icono = models.CharField(max_length=50)   # Nombre de la clase de icono
    orden = models.IntegerField(default=0, help_text="Indica el orden en que se mostrara en el menu")  # Campo para el orden

    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app_postventa'  # Agregar esta línea para indicar la aplicación
        verbose_name = 'Opciones del menu'
        ordering = ['orden']  # Ordenar los registros por el campo 'orden'
    
class Permisos(models.Model):
    nombre = models.CharField(max_length=50)
    opciones_menu = models.ManyToManyField(OpcionMenu)
    opcion_default = models.ForeignKey(OpcionMenu, on_delete=models.SET_NULL, null=True, blank=True, related_name='permiso_default_relacionado')

    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app_postventa'  # Agregar esta línea para indicar la aplicación
        verbose_name = 'Permisos x usuario'
    
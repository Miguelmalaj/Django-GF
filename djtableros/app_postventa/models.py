from django.db import models
from django.contrib.auth.models import Permission
from dashboards.models import empresas

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
    
class Objetivos(models.Model):
    # Asociar el objetivo a una empresa y sucursal
    empresa_sucursal = models.ForeignKey(empresas, on_delete=models.CASCADE)  # Usa tu modelo de empresas
    periodo = models.CharField(max_length=6, help_text="Formato: AAAAMM (por ejemplo, 202309 para septiembre de 2023)")
    venta_refacciones = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Objetivo de ventas de refacciones")
    utilidad_refacciones = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Objetivo de utilidad de refacciones")
    venta_servicio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Objetivo de ventas de servicio")
    utilidad_servicio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Objetivo de utilidad de servicio")

    def __str__(self):
        return f"Objetivo {self.empresa_sucursal} - {self.periodo}"
    
    class Meta:
        app_label = 'app_postventa'  # Agregar esta línea para indicar la aplicación
        verbose_name = 'Objetivos de Postventa'
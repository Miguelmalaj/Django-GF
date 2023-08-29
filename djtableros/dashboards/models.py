from django.db import models
from django.contrib.auth.models import Permission

# Create your models here.
class empresas(models.Model):
    empresa = models.PositiveBigIntegerField()
    sucursal = models.PositiveBigIntegerField(default=1) 
    nombre_empresa = models.CharField(max_length=30, help_text="Indique el nombre de la razon social")
    direccion_ip = models.CharField(max_length=100, help_text="Direccion IP del servidor GlobalDMS")
    usuario = models.CharField(max_length=100)
    clave_acceso = models.CharField(max_length=100)
    ref_cartera = models.CharField(max_length=30, default='*', help_text="Referencia en el campo PRIM_REFERENCIA3 en GlobalDMS para separar la cartera de CXC")

    # def save(self, *args, **kwargs):
    #     # Hasheamos la clave de acceso antes de guardarla
    #     self.clave_acceso = make_password(self.clave_acceso)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_empresa
    
class OpcionMenu(models.Model):
    nombre = models.CharField(max_length=50)
    vista = models.CharField(max_length=100)  # Nombre de la vista
    icono = models.CharField(max_length=50)   # Nombre de la clase de icono

    def __str__(self):
        return self.nombre
    
class Permisos(models.Model):
    nombre = models.CharField(max_length=50)
    opciones_menu = models.ManyToManyField(OpcionMenu)
    opcion_default = models.ForeignKey(OpcionMenu, on_delete=models.SET_NULL, null=True, blank=True, related_name='permiso_default_relacionado')

    def __str__(self):
        return self.nombre
    
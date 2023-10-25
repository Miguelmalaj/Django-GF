from django.db import models

# Create your models here.
class OpcionMenu(models.Model):
    nombre = models.CharField(max_length=50)
    vista = models.CharField(max_length=100)
    icono = models.CharField(max_length=50)
    orden = models.IntegerField(default=0, help_text="Indica el orden en que se mostrara en el menu")

    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app_corporativo'
        verbose_name = 'Opciones del menu'
        ordering = ['orden']


class Permisos(models.Model):
    nombre = models.CharField(max_length=50)
    opciones_menu = models.ManyToManyField(OpcionMenu)
    opcion_default = models.ForeignKey(OpcionMenu, on_delete=models.SET_NULL, null=True, blank=True, related_name='permiso_default_relacionado')

    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app_corporativo'
        verbose_name = 'Permisos x usuario'
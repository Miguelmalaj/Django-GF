from app_postventa.models import Permisos, OpcionMenu

def obtener_opciones_menu_postventa(usuario):
    permisos_usuario = Permisos.objects.filter(nombre=usuario)
    opciones_menu = OpcionMenu.objects.filter(permisos__in=permisos_usuario)
    opciones_menu_list = list(opciones_menu.values('nombre', 'vista', 'icono'))
    return opciones_menu_list

def calcula_porcentaje_valor(valor, total):
    porcentaje = 0
    if total != 0:
        porcentaje =  (valor / total) * 100
    return porcentaje
from app_contabilidad.models import Permisos, OpcionMenu

def obtener_opciones_menu_contabilidad(usuario):
    permisos_usuario = Permisos.objects.filter(nombre=usuario)
    opciones_menu = OpcionMenu.objects.filter(permisos__in=permisos_usuario)
    opciones_menu_list = list(opciones_menu.values('nombre', 'vista', 'icono'))
    return opciones_menu_list

def obtener_opcion_default_conta(usuario):
    try:
        permisos = Permisos.objects.get(nombre=usuario)
        opcion_default = permisos.opcion_default
        return opcion_default
    except Permisos.DoesNotExist:
        return None
    
def calcula_porcentaje_valor(valor, total):
    porcentaje = 0
    if total != 0:
        porcentaje =  (valor / total) * 100
    return porcentaje

def obtiene_opcionmenu(nombrevista):
    try:
        strmenu = OpcionMenu.objects.get(vista=nombrevista)
    except OpcionMenu.DoesNotExist:
        strmenu = "no encontrada"

    return strmenu
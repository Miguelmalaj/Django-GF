from app_postventa.models import Permisos, OpcionMenu, Objetivos
from decimal import Decimal

def obtener_opciones_menu_postventa(usuario):
    permisos_usuario = Permisos.objects.filter(nombre=usuario)
    opciones_menu = OpcionMenu.objects.filter(permisos__in=permisos_usuario)
    opciones_menu_list = list(opciones_menu.values('nombre', 'vista', 'icono'))
    return opciones_menu_list

def obtener_opcion_default(usuario):
    try:
        permisos = Permisos.objects.get(nombre=usuario)
        opcion_default = permisos.opcion_default
        return opcion_default
    except Permisos.DoesNotExist:
        return None
    
def calcula_porcentaje_valor(valor, total):
    porcentaje = Decimal(0)
    if total != Decimal(0):
        porcentaje = (Decimal(valor) / Decimal(total)) * Decimal(100)
    return porcentaje

def obtiene_opcionmenu(nombrevista):
    try:
        strmenu = OpcionMenu.objects.get(vista=nombrevista)
    except OpcionMenu.DoesNotExist:
        strmenu = "no encontrada"

    return strmenu

def obtiene_objetivos(empresa, sucursal, periodo):
    # Realiza la consulta para obtener los objetivos
    objetivos = Objetivos.objects.filter(
        empresa_sucursal__empresa = empresa,
        empresa_sucursal__sucursal = sucursal,
        periodo = periodo
    )

    # Comprobar si se encontraron objetivos
    if objetivos.exists():
        # Si existen objetivos, obtener el primero
        objetivo = objetivos.first()
    else:
        # Si no existen objetivos, asignar un valor predeterminado o None
        objetivo = None  # Puedes asignar otro valor predeterminado si lo prefieres

    return objetivo

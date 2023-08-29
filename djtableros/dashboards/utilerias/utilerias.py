from datetime import datetime
from dashboards.models import Permisos, OpcionMenu

def periodos():
    # Obtener el año actual
    year_actual = datetime.now().year

    # Generar la lista de años desde 2019 hasta el año actual
    years = list(range(2019, year_actual + 1))

    # Renderizar la página y pasar la lista de años al contexto
    return years

def llenar_combo_meses():
    meses = {}
    meses_espanol = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    for numero_mes in range(1, 13):
        nombre_mes_espanol = meses_espanol[numero_mes - 1]
        meses[numero_mes] = nombre_mes_espanol
    return meses

def nombre_mes(numero_mes):
    meses_espanol = ['***', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    return meses_espanol[numero_mes]     

def calcula_porcentaje(real, objetivo):
    """
    funcion para calcular el porcentaje y regresar un diccionario de datos con el real, objetivo y porcentaje
    """
    porcentaje = 0
    if (objetivo !=0):
            porcentaje = f"{(real / objetivo) * 100:.2f}"

    datos = {
            'real': real,
            'objetivo': objetivo,
            'porcentaje': porcentaje
    } 

    return datos

def calcula_porcentaje_valor(real, objetivo):
    """
    funcion para calcular el porcentaje y regresar un solo valor
    """
    porcentaje = float('-inf')
    if (objetivo !=0):
            porcentaje = (real / objetivo) * 100

    return porcentaje

# Función para calcular el porcentaje de avance
def calcular_porcentaje_avance(real, objetivo):
    if objetivo == 0:
        return 0
    return (real / objetivo) * 100

def obtener_opciones_menu(usuario):
    # Obtener los permisos asociados al usuario
    permisos_usuario = Permisos.objects.filter(nombre=usuario)

    # Obtener todas las opciones de menú asociadas a los permisos del usuario
    opciones_menu = OpcionMenu.objects.filter(permisos__in=permisos_usuario)

    # Convertir las opciones de menú a una lista de diccionarios
    opciones_menu_list = list(opciones_menu.values('nombre', 'vista', 'icono'))

    return opciones_menu_list

def obtener_opcion_default(usuario):
    try:
        permisos = Permisos.objects.get(nombre=usuario)
        opcion_default = permisos.opcion_default
        return opcion_default
    except Permisos.DoesNotExist:
        return None
import pandas as pd
import calendar
import pdfkit
import os
import tempfile
from django.shortcuts import render, redirect
from dashboards.utilerias import funciones, utilerias, consultassql, config
from app_postventa.utils import obtener_opciones_menu_postventa, obtener_opcion_default
from app_contabilidad.utils import obtener_opciones_menu_contabilidad, obtener_opcion_default_conta
from app_astilleros.utils import obtener_opciones_menu_astilleros, obtener_opcion_default_astilleros
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse


def login_view(request):
    if request.method == 'POST':
        user = request.POST.get('username')
        passw = request.POST.get('password')

        username = user.upper()
        password = passw.upper()
        
        # Realizar la autenticación del usuario
        user = config.auntentifica_usuario(usuario=username, clave=password)
        if user is not None:
                # Guardar datos del usuario en la sesión
                request.session['user_id'] = user['usuario']
                request.session['username'] = user['nombre']
                request.session['puesto'] = user['puesto']
                request.session['usericon'] = 'admin-lte/dist/img/' + str(user['icono'])

                # Obtener las opciones de menú para el usuario
                opciones_menuvta = utilerias.obtener_opciones_menu(username)
                opciones_menu_postventa = obtener_opciones_menu_postventa(username)
                opciones_menu_contabilidad = obtener_opciones_menu_contabilidad(username)
                opciones_menu_astilleros = obtener_opciones_menu_astilleros(username)
                opciones_menu = {
                        'ventas': opciones_menuvta,
                        'postventa': opciones_menu_postventa,
                        'contable': opciones_menu_contabilidad,
                        'astilleros': opciones_menu_astilleros
                }
                # Almacenar las opciones de menú en la sesión
                request.session['opciones_menu'] = opciones_menu
                
                # buscar en dashsboard la opcion por default
                opcion_default = utilerias.obtener_opcion_default(username)
                if opcion_default:
                        print(opcion_default.vista)# TEST
                        return redirect(opcion_default.vista)
                else:
                        # buscar en la app_postventa la opcion por default
                        opcion_default = obtener_opcion_default(username)
                        if opcion_default:
                                print(opcion_default.vista)# TEST
                                return redirect(opcion_default.vista)
                        else:
                                # buscar en la app_contabilidad la opcion por default
                                opcion_default = obtener_opcion_default_conta(username)
                                if opcion_default:
                                        print(opcion_default.vista)# TEST
                                        return redirect(opcion_default.vista)
                                else:
                                        #return redirect('base')
                                        #buscar en la app_astilleros la opción por default
                                        opcion_default = obtener_opcion_default_astilleros(username)
                                        if opcion_default:
                                                print(opcion_default.vista)# TEST
                                                return redirect(opcion_default.vista)
                                        else:
                                                return redirect('base')
        else:
                messages.error(request, 'Usuario o Clave incorrecta')
    
    return render(request, 'login.html')



def logout_view(request):
        logout(request)
        return redirect('login')

def base(request):
   
    return render(request, 'pagandoplanpiso.html')

def index(request):
    
    return render(request, 'login')
# *************************************************
# Vistas para el area de Ventas
# *************************************************
def funnel_chart(request):
        if request.method == 'POST': 
                seleccion = request.POST.get('empresas')  # Obtener el valor enviado desde la solicitud, el valor de la izq es la empresa y derecha es la sucursal
                mes = int(request.POST.get('mes'))
                year = int(request.POST.get('periodo'))
                bytEmpresa = int(seleccion[:1])
                bytSucursal = int(seleccion[-1:])
        else:    
                seleccion = "11"
                mes = datetime.now().month
                # Si es menor de los primeros 4 dias del mes, mostrar el mes anterior.
                if datetime.now().day < 4:
                        mes = datetime.now().month -1
                year = datetime.now().year
                bytEmpresa = 1
                bytSucursal = 1  

        dia = datetime.now().day
        # Validar si el mes a consultar es diferente del actual, para en ese caso, dar el dia ultimo de cada mes.
        if mes != datetime.now().month:
                resultado = calendar.monthrange(2023, 4)  # Cambia el año (2023) y el mes (4) según tus necesidades
                # El resultado es una tupla con el último día del mes y el número de días en el mes
                dia = resultado[1]
        
        fecha_actual = datetime.now() # Obtener la fecha actual
        fechahoy = fecha_actual.strftime("%m/%d/%y") # Formatear la fecha en mm/dd/yy

        cboperiodos = utilerias.periodos()
        cbomeses = utilerias.llenar_combo_meses
        mesperiodo = str(utilerias.nombre_mes(mes)[:3]) + " " +str(year)[-2:]
        mesperiodant = str(utilerias.nombre_mes(mes)[:3]) + " " +str(year -1)[-2:]

        # intfacturas, intEntregasGMF, intEntregascont, facturasant, entregasant, intdemos, intdemosant = funciones.obtiene_fact_entregas(bytEmpresa, bytSucursal, mes, year, dia)
        datosdms = funciones.obtiene_fact_entregas(bytEmpresa, bytSucursal, mes, year, dia)
        datoshoy, datosacum, objetivos = consultassql.obtiene_afluencia(bytEmpresa, bytSucursal, mes, year, fechahoy)

        # Formatear los valores en cada diccionario de datos
        afluencia = utilerias.calcula_porcentaje(datosacum['afluencia'] + datosacum['citas'],objetivos['afluencia'], datoshoy['afluencia'] + datoshoy['citas'])
        solicitudes = utilerias.calcula_porcentaje(datosacum['solicitudes'],objetivos['solicitudes'], datoshoy['solicitudes'] )
        demos = utilerias.calcula_porcentaje(datosdms['demosacum'],objetivos['demos'], datosdms['demos'])
        aprobadas = utilerias.calcula_porcentaje(datosacum['aprobadas'],objetivos['aprobadas'], datoshoy['aprobadas'])
        facturas = utilerias.calcula_porcentaje(datosdms['ventasacum'],objetivos['facturas'], datosdms['ventas'])
        contratos = utilerias.calcula_porcentaje(datosacum['contratos'],objetivos['contratos'], datoshoy['contratos'])
        entregasgmf = utilerias.calcula_porcentaje(datosdms['entregasgmfacum'],objetivos['entregasgmf'], datosdms['entregasgm'])
        entregascont = utilerias.calcula_porcentaje(datosdms['entregascontacum'],objetivos['entregascont'], datosdms['entregascont'])
        
        # ******************************************
        # ENTREGAS TOTALES
        porcentajeentregas = 0
        if (objetivos['entregascont'] + objetivos['entregasgmf']) != 0:
                porcentajeentregas = f"{((datosdms['entregascontacum'] + datosdms['entregasgmfacum']) / (objetivos['entregascont'] + objetivos['entregasgmf'])) * 100:.2f}"

        datosentregastotales = {
                'real': datosdms['entregascontacum'] + datosdms['entregasgmfacum'],
                'objetivo': objetivos['entregascont'] + objetivos['entregasgmf'],
                'porcentaje': porcentajeentregas,
                'hoy': datosdms['entregascont'] + datosdms['entregasgm'],
        }

        por_sol = 0
        por_aprob = 0
        por_cont = 0

        if afluencia['real'] != 0:
                por_sol = (solicitudes['real']/afluencia['real']) * 100
        if solicitudes['real'] !=0:
                por_aprob = (aprobadas['real'] / solicitudes['real']) * 100
        if aprobadas['real'] != 0:
                por_cont = (contratos['real'] / aprobadas['real']) * 100

        datos = {
                'empresa':seleccion,
                'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
                'opcionmenu': config.obtiene_opcionmenu('funnelventas'),
                'mes':mes,
                'periodoselec':year,
                'cboperiodos':cboperiodos,
                'cbomeses':cbomeses,
                'facturas':facturas,
                'entregasgmf':entregasgmf,
                'entregascont': entregascont,
                'afluencia': afluencia,
                'freshup': datosacum['afluencia'],
                'citascump': datosacum['citas'],
                'agendadas': datosacum['agendadas'],
                'cumplidas': datosacum['cumplidas'],
                'solicitudes': solicitudes,
                'demos': demos,
                'aprobadas': aprobadas,
                'contratos':contratos,
                'entregastotales': datosentregastotales,
                'mesperiodo': mesperiodo,
                'mesperiodoant' : mesperiodant,
                'por_sol': por_sol,
                'por_aprob' : por_aprob,
                'por_cont' : por_cont
                                }
        return render(request, 'funnel_chart.html', {'datos':datos})

def funel_vendedor(request):
        if request.method == 'POST': 
                seleccion = request.POST.get('empresas')  # Obtener el valor enviado desde la solicitud, el valor de la izq es la empresa y derecha es la sucursal
                mes = int(request.POST.get('mes'))
                year = int(request.POST.get('periodo'))
                bytEmpresa = int(seleccion[:1])
                bytSucursal = int(seleccion[-1:])
        else:    
                seleccion = "11"
                mes = datetime.now().month
                # Si es menor de los primeros 4 dias del mes, mostrar el mes anterior.
                if datetime.now().day < 4:
                        mes = datetime.now().month -1
                year = datetime.now().year
                bytEmpresa = 1
                bytSucursal = 1  

        cboperiodos = utilerias.periodos()
        cbomeses = utilerias.llenar_combo_meses
        mesperiodo = str(utilerias.nombre_mes(mes)[:3]) + " " +str(year)[-2:]

        tablavendedores = funciones.obtiene_funel_asesores(bytEmpresa, bytSucursal, mes, year)
        
        datos = {
                'empresa':seleccion,
                'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
                'opcionmenu': config.obtiene_opcionmenu('funnelvendedor'),
                'mes':mes,
                'periodoselec':year,
                'cboperiodos':cboperiodos,
                'cbomeses':cbomeses,
                'tablavendedores':tablavendedores,
                'mesperiodo': mesperiodo
        }

        return render(request, 'funel_vendedor.html', {'datos':datos})

def ventasanuales(request):
        if request.method == 'POST': 
                seleccion = request.POST.get('empresas')  # Obtener el valor enviado desde la solicitud, el valor de la izq es la empresa y derecha es la sucursal
                year = int(request.POST.get('periodo'))
                bytEmpresa = int(seleccion[:1])
                bytSucursal = int(seleccion[-1:])
        else:    
                seleccion = "11"
                year = datetime.now().year
                bytEmpresa = 1
                bytSucursal = 1  
              
        dataframevehiculosbaja, dataframevendedores = funciones.ventas_anuales(bytEmpresa, bytSucursal, year) 
        tablavendedores = dataframevendedores.reset_index().values.tolist
        tablavehiculosbaja = dataframevehiculosbaja.reset_index().values.tolist
        cboperiodos = utilerias.periodos()
        
        datos = {
                'empresa':seleccion,
                'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
                'opcionmenu': config.obtiene_opcionmenu('ventasanuales'),
                'periodoselec':year,
                'cboperiodos':cboperiodos,
                'tablavend':tablavendedores,
                'tablaveh':tablavehiculosbaja
        }

        return render(request, 'ventasanuales.html', {'datos':datos})

def entregasanuales(request):
        if request.method == 'POST': 
                seleccion = request.POST.get('empresas')  # Obtener el valor enviado desde la solicitud, el valor de la izq es la empresa y derecha es la sucursal
                year = int(request.POST.get('periodo'))
                bytEmpresa = int(seleccion[:1])
                bytSucursal = int(seleccion[-1:])
        else:    
                seleccion = "11"
                year = 2023
                bytEmpresa = 1
                bytSucursal = 1  
              
        dataframevehiculos, dataframevendedores = funciones.entregas_anuales(bytEmpresa, bytSucursal, year) 
        tablavendedores = dataframevendedores.reset_index().values.tolist
        tablavehiculos = dataframevehiculos.reset_index().values.tolist
        cboperiodos = utilerias.periodos()

        datos = {
                'empresa':seleccion,
                'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
                'opcionmenu': config.obtiene_opcionmenu('entregasanuales'),
                'periodoselec':year,
                'cboperiodos':cboperiodos,
                'tablavend':tablavendedores,
                'tablaveh':tablavehiculos
        }

        return render(request, 'entregasanuales.html', {'datos':datos})

def ventasvehiculos(request):
        if request.method == 'POST': 
                seleccion = request.POST.get('fecha') 
                fecha = datetime.strptime(seleccion, "%Y-%m-%d").date()
        else:    
                fecha = datetime.today()
        
        seleccion = fecha.strftime( "%Y-%m-%d")

        df_mochis, df_mochisus = funciones.obtiene_ventasvehiculos(1,1, fecha)
        df_gve, df_gveus = funciones.obtiene_ventasvehiculos(3,1, fecha)
        df_zapata, df_zapataus = funciones.obtiene_ventasvehiculos(5,1, fecha)
        df_aero, df_aerous = funciones.obtiene_ventasvehiculos(5,2, fecha)
        df_flotillas, df_flotillasus = funciones.obtiene_ventasvehiculos(5,3, fecha)
        df_cad, df_cadus = funciones.obtiene_ventasvehiculos(7,1, fecha)

        datos = {
                'opcionmenu': config.obtiene_opcionmenu('ventasvehiculos'),
                'mochis':df_mochis.reset_index().values.tolist,
                'mochisus':df_mochisus.reset_index().values.tolist,
                'guasave':df_gve.reset_index().values.tolist,
                'guasaveus':df_gveus.reset_index().values.tolist,
                'zapata':df_zapata.reset_index().values.tolist,
                'zapataus':df_zapataus.reset_index().values.tolist,
                'aero':df_aero.reset_index().values.tolist,
                'aerous':df_aerous.reset_index().values.tolist,
                'flotillas':df_flotillas.reset_index().values.tolist,
                'flotillasus':df_flotillasus.reset_index().values.tolist,
                'cadillac':df_cad.reset_index().values.tolist,
                'cadillacus':df_cadus.reset_index().values.tolist,
                'fechareporte':seleccion
        }
        return render(request, 'ventasvehiculos.html', {'datos':datos})

def ventasvehiculos_detalle(request, bytAgencia, bytSucursal, fechareporte):
        fecha = datetime.strptime(fechareporte, "%Y-%m-%d").date()
        agencia = int(bytAgencia)
        sucursal = int(bytSucursal)
        df_mochis, df_mochisus = funciones.obtiene_ventasvehiculos(agencia,sucursal, fecha)
        dfn_hoy, dfn_acum,  dfn_cancel, dfn_modebasico, dfnvendedor, dfn_tipoventa, dfn_entregas, df_fne, dfu_hoy, dfu_acum, dfu_cancel, dfu_modebasico, dfu_tipoventa, dfu_vendedor = funciones.obtiene_ventasvehiculos_detalle(agencia,sucursal, fecha)
        datos = {
                'nombreempresa': config.obtiene_empresa(agencia, bytSucursal),
                'opcionmenu': config.obtiene_opcionmenu('ventasvehiculos'),
                'mochis':df_mochis.reset_index().values.tolist,
                'mochisus':df_mochisus.reset_index().values.tolist,
                'nuevoshoy':dfn_hoy.reset_index().values.tolist,
                'nuevosacum':dfn_acum.reset_index().values.tolist,
                'cancelhoy':dfn_cancel.reset_index().values.tolist,
                'nuevosmodelo':dfn_modebasico.reset_index().values.tolist,
                'nuevosvend':dfnvendedor.reset_index().values.tolist,
                'nuevostventa':dfn_tipoventa.reset_index().values.tolist,
                'entregas':dfn_entregas.reset_index().values.tolist,
                'fne':df_fne.reset_index().values.tolist,
                'usadoshoy':dfu_hoy.reset_index().values.tolist,
                'usadoscancel':dfu_cancel.reset_index().values.tolist,
                'usadosmodelo':dfu_modebasico.reset_index().values.tolist,
                'usadosvend':dfu_vendedor.reset_index().values.tolist,
                'usadostventa':dfu_tipoventa.reset_index().values.tolist,
                'usadosacum':dfu_acum.reset_index().values.tolist

        }
        return render(request, 'ventasvehiculos_detalle.html', {'datos':datos})

def resumeninvveh(request):
        if request.method == 'POST': 
                seleccion = request.POST.get('empresas')  # Obtener el valor enviado desde la solicitud, el valor de la izq es la empresa y derecha es la sucursal
                bytEmpresa = int(seleccion[:1])
                bytSucursal = int(seleccion[-1:])
        else:    
                seleccion = "11"
                bytEmpresa = 1
                bytSucursal = 1  
        
        if bytEmpresa != 0:
                dataframevehiculos = funciones.resumen_inventario_x_paquete(bytEmpresa, bytSucursal) 
                empresa = config.obtiene_empresa(bytEmpresa, bytSucursal)
                strnombreempresa = empresa.nombre_empresa
        else:
                strnombreempresa = "CONSOLIDADO"
                dataframevehiculos = funciones.resumen_inventario_x_paquete_consolidado()
        
        # Puedes obtener los nombres de las columnas con df_pivot.columns.tolist()
        columnas = dataframevehiculos.columns.tolist()
        tablavehiculos = dataframevehiculos.reset_index().values.tolist

        datos = {
                'empresa':seleccion,
                'nombreempresa': strnombreempresa,
                'opcionmenu': config.obtiene_opcionmenu('resumeninvveh'),
                'datos':tablavehiculos,
                'columnas': columnas
        }

        return render(request, 'resumeninvveh.html', {'datos':datos})

def inventariovehiculos_detalle(request, empresa, sucursal):
        agencia = int(empresa)
        sucursal = int(sucursal)
        if agencia != 0:
                strnombreempresa = config.obtiene_empresa(agencia, sucursal)
                df_inventario, df_usados, propios_nuevos = funciones.inventario_detalle(agencia,sucursal)
        else:
                strnombreempresa = "CONSOLIDADO"
                df_lmm, df_lmmus, propios_lm = funciones.inventario_detalle(1,1)
                df_gve, df_gveus, propios_gve = funciones.inventario_detalle(3,1)
                df_cln, df_clnus, propios_clnz = funciones.inventario_detalle(5,1)
                df_flo, df_flous, propios_flot = funciones.inventario_detalle(5,3)
                df_cad, df_cadus, propios_cad = funciones.inventario_detalle(7,1)
                df_lmm["agencia"] = "MOC"
                df_gve["agencia"] = "GVE"
                df_cln["agencia"] = "CLN"
                df_cad["agencia"] = "CAD"

                df_lmmus["agencia"] = "MOC"
                df_gveus["agencia"] = "GVE"
                df_clnus["agencia"] = "CLN"
                df_cadus["agencia"] = "CAD"

                df_inventario = pd.concat([df_lmm, df_gve, df_cln, df_flo, df_cad], axis= 0)
                df_usados = pd.concat([df_lmmus, df_gveus, df_clnus, df_flous, df_cadus], axis= 0)
                propios_nuevos = propios_lm + propios_gve + propios_clnz + propios_flot + propios_cad

        # Se regresa el inventario en diccionario de datos, para que en el template podamos 
        # accesar a cada registro por su nombre de columna. ( modificado el 14 de Agosto )
        # los templates anteriores se regresan como lista y se accede a ellos por ciclos for 
        # para los registros y para las columnas
        datos = {
                'nombreempresa': strnombreempresa,
                'opcionmenu': config.obtiene_opcionmenu('inventariovehiculos'),
                'inventario':df_inventario.to_dict(orient='records'),                 
                'totalveh':df_inventario.shape[0],
                'usados':df_usados.to_dict(orient='records'), 
                'totalusados':df_usados.shape[0],
                'propiosnuevos': propios_nuevos,
                'empresa': empresa,
                'sucursal': sucursal
        }
        return render(request, 'inventariovehdetalle.html', {'datos':datos})

def inventariovehiculospdf_detalle(request, empresa, sucursal, tipo):

        agencia = int(empresa)
        sucursal = int(sucursal)
        if agencia != 0:
                strnombreempresa = config.obtiene_empresa(agencia, sucursal)
                df_inventario, df_usados, propios_nuevos = funciones.inventario_detalle(agencia,sucursal)
        else:
                strnombreempresa = "CONSOLIDADO"
                df_lmm, df_lmmus, propios_lm = funciones.inventario_detalle(1,1)
                df_gve, df_gveus, propios_gve = funciones.inventario_detalle(3,1)
                df_cln, df_clnus, propios_clnz = funciones.inventario_detalle(5,1)
                df_flo, df_flous, propios_flot = funciones.inventario_detalle(5,3)
                df_cad, df_cadus, propios_cad = funciones.inventario_detalle(7,1)
                df_lmm["agencia"] = "MOC"
                df_gve["agencia"] = "GVE"
                df_cln["agencia"] = "CLN"
                df_cad["agencia"] = "CAD"

                df_lmmus["agencia"] = "MOC"
                df_gveus["agencia"] = "GVE"
                df_clnus["agencia"] = "CLN"
                df_cadus["agencia"] = "CAD"

                df_inventario = pd.concat([df_lmm, df_gve, df_cln, df_flo, df_cad], axis= 0)
                df_usados = pd.concat([df_lmmus, df_gveus, df_clnus, df_flous, df_cadus], axis= 0)
                propios_nuevos = propios_lm + propios_gve + propios_clnz + propios_flot + propios_cad
        
        datos = {
                'nombreempresa': strnombreempresa,
                'opcionmenu': config.obtiene_opcionmenu('inventariovehiculos'),
                'inventario':df_inventario.to_dict(orient='records'),                 
                'totalveh':df_inventario.shape[0],
                'usados':df_usados.to_dict(orient='records'), 
                'totalusados':df_usados.shape[0],
                'propiosnuevos': propios_nuevos,
        }


        rendered_template = render(
                request, 
                'inventariovehdetallepdf_nuevos.html' if tipo == 'nuevos' else 'inventariovehdetallepdf_seminuevos.html', 
                {'datos':datos}
        )

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
            temp_html.write(rendered_template.content)

        options = {
         'page-size': 'A4',
         'orientation': 'Landscape',
        }

        pdf_filename = tempfile.mktemp(suffix='.pdf')
        pdfkit.from_file(temp_html.name, pdf_filename, options=options)

        os.remove(temp_html.name)

        tiporeporte = "_inventario_nuevos.pdf" if tipo == 'nuevos' else "_inventario_seminuevos.pdf";

        strnombrearchivo = "attachment; filename=" + str(strnombreempresa.nombre_empresa) + tiporeporte

        # Create an HTTP response with the PDF content
        with open(pdf_filename, 'rb') as pdf_file:
             response = HttpResponse(pdf_file.read(), content_type='application/pdf')

        response['Content-Disposition'] = strnombrearchivo
        return response

def inventarioveh(request):

        datoslmm = funciones.resumeninvxagencia(1, 1)                      
        datosgve = funciones.resumeninvxagencia(3, 1)
        datoscln = funciones.resumeninvxagencia(5, 1)
        datosflo = funciones.resumeninvxagencia(5, 3)
        datoscad = funciones.resumeninvxagencia(7, 1)

        # Lista de las cuatro variables para iterar
        variables = [datoslmm, datosgve, datoscln, datoscad]
        # Llave a comparar
        llave = 'diasmas'
        # Inicializa el valor máximo con un valor muy pequeño
        valor_mas_antiguo = float('-inf')
        # Itera a través de las variables y encuentra el valor más grande en la llave 'diasmas'
        for variable in variables:
                if llave in variable and variable[llave] > valor_mas_antiguo:
                        valor_mas_antiguo = variable[llave]
       
        # Realiza la suma de cada campo en las cuatro variables
        datosconsolidado = {
        'nombre_empresa': "CONSOLIDADO", 
        'empresa': '0',
        'sucursal': '0',       
        'totalinv': datoslmm['totalinv'] + datosgve['totalinv'] + datoscln['totalinv'] + datoscad['totalinv'],
        'nu': datoslmm['nu'] + datosgve['nu'] + datoscln['nu'] + datoscad['nu'],
        'de': datoslmm['de'] + datosgve['de'] + datoscln['de'] + datoscad['de'],
        'us': datoslmm['us'] + datosgve['us'] + datoscln['us'] + datoscad['us'],
        'diasmas': valor_mas_antiguo,
        'prom': (datoslmm['prom'] + datosgve['prom'] + datoscln['prom'] + datoscad['prom']) / 4 ,
        'vencidos': datoslmm['vencidos'] + datosgve['vencidos'] + datoscln['vencidos'] + datoscad['vencidos'],
        '30': datoslmm['30'] + datosgve['30'] + datoscln['30'] + datoscad['30'],
        '30porc': (datoslmm['30porc'] + datosgve['30porc'] + datoscln['30porc'] + datoscad['30porc']) / 4,
        '90': datoslmm['90'] + datosgve['90'] + datoscln['90'] + datoscad['90'],
        '90porc': (datoslmm['90porc'] + datosgve['90porc'] + datoscln['90porc'] + datoscad['90porc']) / 4,
        '180': datoslmm['180'] + datosgve['180'] + datoscln['180'] + datoscad['180'],
        '180porc': (datoslmm['180porc'] + datosgve['180porc'] + datoscln['180porc'] + datoscad['180porc']) / 4,
        'propios': datoslmm['propios'] + datosgve['propios'] + datoscln['propios'] + datoscad['propios'],
        'propios_nu': datoslmm['propios_nu'] + datosgve['propios_nu'] + datoscln['propios_nu'] + datoscad['propios_nu'],
        'propios_de': datoslmm['propios_de'] + datosgve['propios_de'] + datoscln['propios_de'] + datoscad['propios_de'],
        'propios_us': datoslmm['propios_us'] + datosgve['propios_us'] + datoscln['propios_us'] + datoscad['propios_us'],
        'propios_importe': datoslmm['propios_importe'] + datosgve['propios_importe'] + datoscln['propios_importe'] + datoscad['propios_importe'],
        'logo':"admin-lte/dist/img/logo_cadchev.jpg",
        'bg': "bg-lightblue"
        }

        datos = {
                'opcionmenu': config.obtiene_opcionmenu('inventariovehiculos'),
                'mochis': datoslmm,
                'guasave': datosgve,
                'culiacan': datoscln,
                'flotillas': datosflo,
                'cadillac': datoscad,
                'grupo': datosconsolidado
        }
        return render(request, 'inventariovehiculos.html', {'datos':datos})

def planpisopagado(request):

        datoslmm = funciones.resumeninvxagencia(1, 1)                      
        datosgve = funciones.resumeninvxagencia(3, 1)
        datoscln = funciones.resumeninvxagencia(5, 1)
        datosflo = funciones.resumeninvxagencia(5, 3)
        datoscad = funciones.resumeninvxagencia(7, 1)

        # Lista de las cuatro variables para iterar
        variables = [datoslmm, datosgve, datoscln, datoscad]
        # Llave a comparar
        llave = 'diasmas'
        # Inicializa el valor máximo con un valor muy pequeño
        valor_mas_antiguo = float('-inf')
        # Itera a través de las variables y encuentra el valor más grande en la llave 'diasmas'
        for variable in variables:
                if llave in variable and variable[llave] > valor_mas_antiguo:
                        valor_mas_antiguo = variable[llave]
       
        # Realiza la suma de cada campo en las cuatro variables
        datosconsolidado = {
        'nombre_empresa': "CONSOLIDADO", 
        'empresa': '0',
        'sucursal': '0',       
        'totalinv': datoslmm['totalinv'] + datosgve['totalinv'] + datoscln['totalinv'] + datoscad['totalinv'],
        'nu': datoslmm['nu'] + datosgve['nu'] + datoscln['nu'] + datoscad['nu'],
        'de': datoslmm['de'] + datosgve['de'] + datoscln['de'] + datoscad['de'],
        'us': datoslmm['us'] + datosgve['us'] + datoscln['us'] + datoscad['us'],
        'diasmas': valor_mas_antiguo,
        'prom': (datoslmm['prom'] + datosgve['prom'] + datoscln['prom'] + datoscad['prom']) / 4 ,
        'vencidos': datoslmm['vencidos'] + datosgve['vencidos'] + datoscln['vencidos'] + datoscad['vencidos'],
        '30': datoslmm['30'] + datosgve['30'] + datoscln['30'] + datoscad['30'],
        '30porc': (datoslmm['30porc'] + datosgve['30porc'] + datoscln['30porc'] + datoscad['30porc']) / 4,
        '90': datoslmm['90'] + datosgve['90'] + datoscln['90'] + datoscad['90'],
        '90porc': (datoslmm['90porc'] + datosgve['90porc'] + datoscln['90porc'] + datoscad['90porc']) / 4,
        '180': datoslmm['180'] + datosgve['180'] + datoscln['180'] + datoscad['180'],
        '180porc': (datoslmm['180porc'] + datosgve['180porc'] + datoscln['180porc'] + datoscad['180porc']) / 4,
        'logo':"admin-lte/dist/img/logo_cadchev.jpg",
        'bg': "bg-lightblue"
        }

        datos = {
                'opcionmenu': config.obtiene_opcionmenu('inventariovehiculos'),
                'mochis': datoslmm,
                'guasave': datosgve,
                'culiacan': datoscln,
                'flotillas': datosflo,
                'cadillac': datoscad,
                'grupo': datosconsolidado
        }
        return render(request, 'inventariovehiculos.html', {'datos':datos})


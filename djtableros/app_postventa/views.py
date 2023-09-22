import pandas as pd
from django.shortcuts import render, redirect
from dashboards.utilerias import config, utilerias
from datetime import datetime
from . import consultas, utils

# Create your views here.
def index(request):
    
    return render(request, 'base.html')

# Create your views here.
def resumenpostventa(request):
    if request.method == 'POST': 
            seleccion = request.POST.get('fecha') 
            fecha = datetime.strptime(seleccion, "%Y-%m-%d").date()
    else:    
            fecha = datetime.today()
    
    seleccion = fecha.strftime( "%Y-%m-%d")
    
    datoslmm = consultas.obtener_resumenpostventa(1, 1, fecha)
    datosgve = consultas.obtener_resumenpostventa(3, 1, fecha)
    datoscln = consultas.obtener_resumenpostventa(5, 1, fecha)
    datosaer = consultas.obtener_resumenpostventa(5, 2, fecha)
    datoscad = consultas.obtener_resumenpostventa(7, 1, fecha)

    datos = {
                'opcionmenu': utils.obtiene_opcionmenu('resumenpostventa'),
                'mochis': datoslmm,
                'guasave': datosgve,
                'culiacan': datoscln,
                'aeropuerto': datosaer,
                'cadillac': datoscad,
                'grupo': 0,
                'fechareporte':seleccion
        }
    return render(request, 'resumenpostventa.html', {'datos':datos})


def ventaservicio(request):
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

    df_mo, df_tot, df_internas, df_total, df_grupomo, df_grupotot, df_grupointerna, df_tktpromor, df_tktasesor, df_totales, df_totalasesor = consultas.obtener_ventaservicio(bytEmpresa, bytSucursal, mes, year)

    datos = {
        'empresa':seleccion,
        'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
        'opcionmenu': utils.obtiene_opcionmenu('ventaservicio'),
        'mes':mes,
        'periodoselec':year,
        'cboperiodos':cboperiodos,
        'cbomeses':cbomeses,
        'mesperiodo': mesperiodo,
        'manoobra': df_mo.to_dict(orient='records'), 
        'tot': df_tot.to_dict(orient='records'), 
        'internas': df_internas.to_dict(orient='records'), 
        'total': df_total.to_dict(orient='records'),
        'grupomo': df_grupomo.to_dict(orient='records'),
        'grupotot': df_grupotot.to_dict(orient='records'),
        'grupoint': df_grupointerna.to_dict(orient='records'),
        'tktorden': df_tktpromor.to_dict(orient='records'),
        'tktasesor': df_tktasesor.to_dict(orient='records'),
        'df_totales': df_totales.to_dict(orient='records'),
        'df_totalasesor': df_totalasesor.to_dict(orient='records')
    }

    return render(request, 'venta_servicio.html', {'datos':datos})

def ordenesproceso(request):
    if request.method == 'POST': 
        seleccion = request.POST.get('empresas')  # Obtener el valor enviado desde la solicitud, el valor de la izq es la empresa y derecha es la sucursal
        
        bytEmpresa = int(seleccion[:1])
        bytSucursal = int(seleccion[-1:])
    else:    
        seleccion = "11"
        
        bytEmpresa = 1
        bytSucursal = 1  
        
    df_ordenes, df_ordenes_status, df_ordenes_tipo= consultas.obtener_ordenesproceso(bytEmpresa, bytSucursal)

    datos = {
        'empresa':seleccion,
        'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
        'opcionmenu': utils.obtiene_opcionmenu('ordenesproceso'),
        'total': df_ordenes.to_dict(orient='records'), 
        'status': df_ordenes_status.to_dict(orient='records'), 
        'concepto': df_ordenes_tipo.to_dict(orient='records')
    }

    return render(request, 'ordenes_proceso.html', {'datos':datos})

def ventarefacciones(request):
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

    utilref, porcref, utilser, porcser, utilinterna, porcinterna, ventatotal, utiltotal, porctotal = consultas.obtener_resumen_ventarefacciones(bytEmpresa, bytSucursal, mes, year)
    df_refacciones_tipovta, df_servicio_tipovta, df_servicio_internas, df_refacciones_ventamostrador = consultas.obtener_ventarefacciones(bytEmpresa, bytSucursal, mes, year)
    resumen = {
        'utilref':utilref, 
        'porcref':porcref, 
        'utilser':utilser, 
        'porcser':porcser, 
        'utilinterna':utilinterna, 
        'porcinterna':porcinterna, 
        'ventatotal':ventatotal, 
        'utiltotal':utiltotal, 
        'porctotal':porctotal
    }
    
    # Solo en aeropuerto la sucursal la maneja globalDMS como 3, hay que cambiarla a 2 para que obtenga el nombre correcto de la empresa
    if bytSucursal == 3:
         bytSucursal = 2

    datos = {
        'empresa':seleccion,
        'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
        'opcionmenu': utils.obtiene_opcionmenu('ventarefacciones'),
        'mes':mes,
        'periodoselec':year,
        'cboperiodos':cboperiodos,
        'cbomeses':cbomeses,
        'mesperiodo': mesperiodo,
        'resumen': resumen,
        'refa': df_refacciones_tipovta.to_dict(orient='records'),
        'servicio': df_servicio_tipovta.to_dict(orient='records'),
        'internas': df_servicio_internas.to_dict(orient='records'),
        'mostrador': df_refacciones_ventamostrador.to_dict(orient='records')
    }
    return render(request, 'venta_refacciones.html', {'datos': datos})

def detalle_ordenes(request, empresa, tipo_orden, year, mes, tipoconsulta):
    bytEmpresa = int(empresa[:1])
    bytSucursal = int(empresa[-1:])

    if bytSucursal == 3:
         bytSucursal = 2

    # obtener el nombre del menu dependiendo del tipo de consulta que se esta ejecutando.
    opcionmenu = 'ventaservicio'
    if tipoconsulta == 3:  
         opcionmenu = 'ordenesproceso'

    df_resultado = consultas.obtiene_detalle_ordenes_facturadas(bytEmpresa, bytSucursal, tipo_orden, year, mes, tipoconsulta)
    datos = {
        'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
        'opcionmenu': utils.obtiene_opcionmenu(opcionmenu),
        'tipoorden': tipo_orden,
        'tablaordenes': df_resultado.to_dict(orient='records')
    }

    return render(request, 'detalle_ordenes.html', {'datos':datos})

def detalle_mostrador(request, empresa, concepto, year, mes, tipoconsulta):
    bytEmpresa = int(empresa[:1])
    bytSucursal = int(empresa[-1:])

    df_resultado = consultas.obtener_detalleventarefacciones(bytEmpresa, bytSucursal, concepto, year, mes, tipoconsulta)

    # Solo en aeropuerto la sucursal la maneja globalDMS como 3, hay que cambiarla a 2 para que obtenga el nombre correcto de la empresa
    if bytSucursal == 3:
         bytSucursal = 2
    
    datos = {
        'nombreempresa': config.obtiene_empresa(bytEmpresa, bytSucursal),
        'opcionmenu': utils.obtiene_opcionmenu('ventarefacciones'),
        'concepto': concepto,
        'tablaordenes': df_resultado.to_dict(orient='records')
    }

    return render(request, 'detalle_refacciones.html', {'datos':datos}) 
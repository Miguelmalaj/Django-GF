from dashboards.utilerias import config
from django.shortcuts import render, redirect
from app_contabilidad import consultas, utils

# Create your views here.
def index(request):
    
    return render(request, 'base.html')

def cuentasxcobrar(request):
        
        datoslmm = consultas.resumen_cuentasxcobrar(1, 1)                      
        datosgve = consultas.resumen_cuentasxcobrar(3, 1)
        datoscln = consultas.resumen_cuentasxcobrar(5, 1)
        datosaer = consultas.resumen_cuentasxcobrar(5, 2)
        datosflo = consultas.resumen_cuentasxcobrar(5, 3)     
        datoscad = consultas.resumen_cuentasxcobrar(7, 1)

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

        datos = {
                'opcionmenu': utils.obtiene_opcionmenu('cuentasxcobrar'),
                'mochis': datoslmm,
                'guasave': datosgve,
                'culiacan': datoscln,
                'aeropuerto': datosaer,
                'flotillas':datosflo,
                'cadillac': datoscad
        }
        return render(request, 'cuentasxcobrar.html', {'datos':datos})

def cuentasxcobrar_detalle(request, empresa, sucursal):
        agencia = int(empresa)
        sucursal = int(sucursal)
        if agencia != 0:
                strnombreempresa = config.obtiene_empresa(agencia, sucursal)
                df_resultado = consultas.detalle_cuentasxcobrar(agencia,sucursal)
        
                datos = {
                        'nombreempresa': strnombreempresa,
                        'opcionmenu': utils.obtiene_opcionmenu('cuentasxcobrar'),
                        'cuentasxcobrar':df_resultado.to_dict(orient='records')
                }
        return render(request, 'cuentasxcobrardetalle.html', {'datos':datos})



def cuentasxpagar(request):
        
        datoslmm = consultas.resumen_cuentasxpagar(1, 1)                      
        datosgve = consultas.resumen_cuentasxpagar(3, 1)
        datoscln = consultas.resumen_cuentasxpagar(5, 1)
        datosaer = consultas.resumen_cuentasxpagar(5, 2)
        datoscad = consultas.resumen_cuentasxpagar(7, 1)

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

        datos = {
                'opcionmenu': utils.obtiene_opcionmenu('cuentasxpagar'),
                'mochis': datoslmm,
                'guasave': datosgve,
                'culiacan': datoscln,
                'aeropuerto': datosaer,
                'cadillac': datoscad
        }
        return render(request, 'cuentasxpagar.html', {'datos':datos})

def cuentasxpagar_detalle(request, empresa, sucursal):
        agencia = int(empresa)
        sucursal = int(sucursal)
        if agencia != 0:
                strnombreempresa = config.obtiene_empresa(agencia, sucursal)
                df_resultado = consultas.detalle_cuentasxpagar(agencia,sucursal)
        
                datos = {
                        'nombreempresa': strnombreempresa,
                        'opcionmenu': utils.obtiene_opcionmenu('cuentasxpagar'),
                        'cuentasxpagar':df_resultado.to_dict(orient='records')
                }
        return render(request, 'cuentasxpagardetalle.html', {'datos':datos})


import pdfkit
import os
from django.http import HttpResponse
from dashboards.utilerias import config
from django.shortcuts import render, redirect
from app_contabilidad import consultas, utils
import tempfile


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
                        'cuentasxcobrar':df_resultado.to_dict(orient='records'),
                        'empresa': empresa,
                        'sucursal': sucursal
                }
        return render(request, 'cuentasxcobrardetalle.html', {'datos':datos})

def cuentasxcobrarpdf_detalle(request, empresa, sucursal):
        agencia = int(empresa)
        sucursal = int(sucursal)
        if agencia != 0:
                strnombreempresa = config.obtiene_empresa(agencia, sucursal)
                df_resultado = consultas.detalle_cuentasxcobrar(agencia,sucursal)
        
                datos = {
                        'nombreempresa': strnombreempresa,
                        'opcionmenu': utils.obtiene_opcionmenu('cuentasxcobrar'),
                        'cuentasxcobrar':df_resultado.to_dict(orient='records'),
                        'empresa': empresa,
                        'sucursal': sucursal
                }

        rendered_template = render(request, 'cuentasxcobrardetallepdf.html', {'datos':datos})

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html.write(rendered_template.content)

        options = {
         'page-size': 'A4',
         'orientation': 'Landscape',
        }

        pdf_filename = tempfile.mktemp(suffix='.pdf')
        pdfkit.from_file(temp_html.name, pdf_filename, options=options)

        os.remove(temp_html.name)


        # Create an HTTP response with the PDF content
        with open(pdf_filename, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')

        response['Content-Disposition'] = 'attachment; filename="cuentasxcobrar_detalles.pdf"'
        return response

def generatepdf_cuentasxcobrar(request):

        datoslmm = consultas.resumen_cuentasxcobrar(1, 1)                      
        datosgve = consultas.resumen_cuentasxcobrar(3, 1)
        datoscln = consultas.resumen_cuentasxcobrar(5, 1)
        datosaer = consultas.resumen_cuentasxcobrar(5, 2)
        datosflo = consultas.resumen_cuentasxcobrar(5, 3)     
        datoscad = consultas.resumen_cuentasxcobrar(7, 1)
        
        variables = [datoslmm, datosgve, datoscln, datoscad]
        
        llave = 'diasmas'
        
        valor_mas_antiguo = float('-inf')
        
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

        rendered_template = render(request, 'templatetest.html', {'datos':datos}) 
        # rendered_template = render(request, 'cuentasxcobrar.html', {'datos':datos}) 
        # rendered_template = render(request, 'base.html') 

        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
            temp_html.write(rendered_template.content)

        # Path to the HTML template file
        # html_template = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')
        #       html_template = os.path.dirname(__file__) + '/templates/base.html'


        # Output file path for the PDF
        # pdf_file = os.path.dirname(__file__) + '/docs/output.pdf'

        # Configure options for wkhtmltopdf (optional)
        # 'page-size': 'letter',

        
        options = {
                'page-size': 'A4',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
        }

        # Convert HTML to PDF using pdfkit
        # pdfkit.from_file(html_template, pdf_file, options=options)
        # pdfkit.from_file(rendered_template, pdf_file, options=options)

        
        pdf_filename = tempfile.mktemp(suffix='.pdf')
        pdfkit.from_file(temp_html.name, pdf_filename)
        # pdf = pdfkit.from_file(rendered_template, False)

        
        os.remove(temp_html.name)

        

        # Create an HTTP response with the PDF content
        with open(pdf_filename, 'rb') as pdf_file:
          response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        
        response['Content-Disposition'] = 'attachment; filename="output.pdf"'
        return response

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
                        'cuentasxpagar':df_resultado.to_dict(orient='records'),
                        'empresa': empresa,
                        'sucursal': sucursal
                }
        return render(request, 'cuentasxpagardetalle.html', {'datos':datos})

def cuentasxpagarpdf_detalle(request, empresa, sucursal):
        agencia = int(empresa)
        sucursal = int(sucursal)
        if agencia != 0:
                strnombreempresa = config.obtiene_empresa(agencia, sucursal)
                df_resultado = consultas.detalle_cuentasxpagar(agencia,sucursal)
        
                datos = {
                        'nombreempresa': strnombreempresa,
                        'opcionmenu': utils.obtiene_opcionmenu('cuentasxpagar'),
                        'cuentasxpagar':df_resultado.to_dict(orient='records'),
                        'empresa': empresa,
                        'sucursal': sucursal
                }
        rendered_template = render(request, 'cuentasxpagardetallepdf.html', {'datos':datos})

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html.write(rendered_template.content)

        options = {
         'page-size': 'A4',
         'orientation': 'Landscape',
        }

        pdf_filename = tempfile.mktemp(suffix='.pdf')
        pdfkit.from_file(temp_html.name, pdf_filename, options=options)

        os.remove(temp_html.name)

        # Create an HTTP response with the PDF content
        with open(pdf_filename, 'rb') as pdf_file:
             response = HttpResponse(pdf_file.read(), content_type='application/pdf')

        response['Content-Disposition'] = 'attachment; filename="cuentasxpagar_detalles.pdf"'
        return response
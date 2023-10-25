from django.shortcuts import render
from django.http import HttpResponse
from app_corporativo import utils, consultas
from datetime import datetime
import tempfile
import pdfkit
import os

# Create your views here.
def index(request):
    return render(request, 'base.html')

def cxcautoleasing(request):

    if request.method == 'POST':
        seleccion = request.POST.get('fecha')
        year, month, day = seleccion.split('-')
        fecha = datetime(int(year), int(month), int(day))
    else:
        fecha = datetime.today()

    agencia = 8
    sucursal = 1
    strnombreempresa = "CORPORATIVO"
    seleccion = fecha.strftime("%Y-%m-%d")

    cxcautoleasing = consultas.detalle_cuentasxcobrar(agencia, sucursal, fecha)

    datos = {
        'nombreempresa': strnombreempresa,
        'opcionmenu': utils.obtiene_opcionmenu('cxcautoleasing'),
        'cxcautoleasing': cxcautoleasing.to_dict(orient='records'),
        'fechareporte': seleccion,
        'empresa': agencia,
        'sucursal': sucursal
    }

    return render(request, 'cxcautoleasing.html', {'datos': datos})

def cxcautoleasing_pdf(request):
    agencia = 8
    sucursal = 1
    strnombreempresa = "CORPORATIVO"
    tstdate = '2023-10-17'

    cxcautoleasing = consultas.detalle_cuentasxcobrar(agencia, sucursal, tstdate)

    datos = {
        'nombreempresa': strnombreempresa,
        'opcionmenu': utils.obtiene_opcionmenu('cxcautoleasing'),
        'cxcautoleasing': cxcautoleasing.to_dict(orient='records'),
        'empresa': agencia,
        'sucursal': sucursal
    }

    rendered_template = render(request, 'cxcautoleasingpdf.html', {'datos': datos})

    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
            temp_html.write(rendered_template.content)

    # Opciones para pdfkit
    options = {
    'page-size': 'Letter',  # Tamaño de página (puede personalizarse)
    'orientation': 'Landscape',  # Orientación horizontal (landscape)
    'margin-top': '5mm',
    'margin-right': '5mm',
    'margin-bottom': '5mm',
    'margin-left': '5mm',
    }

    pdf_filename = tempfile.mktemp(suffix='.pdf')
    pdfkit.from_file(temp_html.name, pdf_filename, options=options)

    os.remove(temp_html.name)

    strnombrearchivo = "attachment; filename=" + str(strnombreempresa) + "_cxcautoleasing.pdf"
    # Create an HTTP response with the PDF content
    with open(pdf_filename, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')

    response['Content-Disposition'] = strnombrearchivo
    return response

def inmobiliaria(request):

    strnombreempresa = "CORPORATIVO"

    df_ocupacion_plazas, df_ocupacion_otros_inmuebles = consultas.detalle_inmobiliaria()
     
    datos = {
        'nombreempresa': strnombreempresa,
        'opcionmenu': utils.obtiene_opcionmenu('inmobiliaria'),
        'df_ocupacion_plazas': df_ocupacion_plazas.to_dict(orient='records'),
        'df_ocupacion_otros_inmuebles': df_ocupacion_otros_inmuebles.to_dict(orient='records'),
    }

    return render(request, 'inmobiliaria.html', {'datos': datos})

def inmobiliaria_detalle(request):
     # Recibirá otros parámetros.
     strnombreempresa = "CORPORATIVO"

     df_ocupacion_detalle = consultas.detalle_completo_inmobiliaria()

     datos = {
          'nombreempresa': strnombreempresa,
          'opcionmenu': utils.obtiene_opcionmenu('inmobiliaria'),
          'df_ocupacion_detalle': df_ocupacion_detalle.to_dict(orient='records')
     }

     return render(request, 'inmobiliaria_detalle.html', {'datos': datos})
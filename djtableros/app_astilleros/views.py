from django.shortcuts import render
from django.http import HttpResponse
from app_astilleros import consultas, utils
from datetime import datetime
import tempfile
import pdfkit
import os

# Create your views here.
def index(request):
    return render(request, 'base.html')

def informegerencial(request):
    if request.method == 'POST':
         seleccion = request.POST.get('fecha')
         year, month, day = seleccion.split('-')
         fecha = datetime(int(year), int(month), int(day))

    else:
        fecha = datetime.today()

    agencia = 1
    sucursal = 1
    strnombreempresa = "ASTILLEROS MARINA TOPOLOBAMPO"        
    seleccion = fecha.strftime("%Y-%m-%d")

    df_cap_instalada, df_efi_cobranza = consultas.reporte_objetivos(agencia, sucursal, fecha)

    datos = {
        'nombreempresa': strnombreempresa,
        'opcionmenu': utils.obtiene_opcionmenu('informegerencial'),
        'capacidadinstalada': df_cap_instalada.to_dict(orient='records'),
        'eficienciacobranza': df_efi_cobranza.to_dict(orient='records'),
        'empresa': agencia,
        'sucursal': sucursal,
        'fechareporte':seleccion
    }

    return render(request, 'informegerencial.html', {'datos': datos})

def cxcastilleros(request):
    agencia = 1;
    sucursal = 1;
    strnombreempresa = "ASTILLEROS MARINA TOPOLOBAMPO"

    df_resultado = consultas.detalle_cuentasxcobrar(agencia, sucursal)

    datos = {
        'nombreempresa': strnombreempresa,
        'opcionmenu': utils.obtiene_opcionmenu('cxcastilleros'),
        'cxcastilleros': df_resultado.to_dict(orient='records'),
        'empresa': agencia,
        'sucursal': sucursal
    }

    return render(request, 'cxcastilleros.html', {'datos': datos})

def cxcastilleros_pdf(request):
    agencia = 1;
    sucursal = 1;
    strnombreempresa = "ASTILLEROS MARINA TOPOLOBAMPO"

    df_resultado = consultas.detalle_cuentasxcobrar(agencia, sucursal)

    datos = {
        'nombreempresa': strnombreempresa,
        'opcionmenu': utils.obtiene_opcionmenu('cxcastilleros'),
        'cxcastilleros': df_resultado.to_dict(orient='records'),
        'empresa': agencia,
        'sucursal': sucursal
    }

    rendered_template = render(request, 'cxcastillerospdf.html', {'datos': datos})

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

    strnombrearchivo = "attachment; filename=" + str(strnombreempresa) + "_cxcastilleros.pdf"
    # Create an HTTP response with the PDF content
    with open(pdf_filename, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')

    response['Content-Disposition'] = strnombrearchivo
    return response


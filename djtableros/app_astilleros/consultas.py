from dashboards.utilerias import configsql
from datetime import datetime
import pandas as pd
import numpy as np
from decimal import Decimal

def detalle_cuentasxcobrar(bytAgencia, bytSucursal):
    """
    Obtiene el resumen de las cuentas x cobrar de astilleros.
    """
    conn = None
    # Crea conexión a BD.
    conn = configsql.creaconeccionsqlM()

    # Crea un cursor.
    c = conn.cursor()

    proc_almacenado = "spC_Saldos_cxc_tableros"
    # fecha = '2023-10-11';
    fecha = datetime.now()

    c.callproc(proc_almacenado, (bytAgencia, bytSucursal, fecha))

    resultados = c.fetchall()

    c.close()
    conn.close()
    
    df_consulta = pd.DataFrame.from_records(resultados)
    df_consulta.columns = ['cliente', 'nombre', 'importe', 'totalcxc', 'vigente', '30','60', '90', 'mas_90', 'totalvencido']

    # Agrupar el DataFrame df_totals por cliente y grupocartera, concatenando los comentarios
    df_grouped_totals = df_consulta.groupby(['cliente']).agg({
        'nombre': 'first',  # Tomar el primer valor del nombre
        'importe': 'sum',
        'totalcxc': 'sum',
        'vigente': 'sum',
        '30': 'sum',
        '60': 'sum',
        '90': 'sum',
        'mas_90': 'sum',
        'totalvencido': 'sum'
    }).reset_index()


    # Calcular los totales para la fila "TOTAL"
    total_row = df_grouped_totals.drop(['cliente'], axis=1).sum().fillna(0)
    total_row['nombre'] = 'TOTAL CARTERA'  # Agregar el nombre "TOTAL"
    
    # Crear un DataFrame con la fila "TOTAL"
    df_total_row = pd.DataFrame([total_row], columns=df_grouped_totals.columns)

    # Concatenar df_grouped_totals y df_total_row
    df_final = pd.concat([df_grouped_totals, df_total_row], ignore_index=True).fillna(' ')

    # Ordenar primero por la columna 'Edad' de forma descendente y luego por 'Puntuación' de forma ascendente
    df_final = df_final.sort_values(by=['totalvencido', 'totalcxc'], ascending=[False, False])

    return df_final

def reporte_objetivos(bytAgencia, bytSucursal, dateSelected):
    """
    Obtiene el resumen de objetivos, capacidad instalada.
    """

    conn = None

    # Crea conexión a BD.
    conn = configsql.creaconeccionsqlM()

    # Crea un cursor.
    c = conn.cursor()

    proc_almacenado_spy_obj = "spy_Rep_Objetivos"
    proc_almacenado_spy_obj_cobr = "spy_Rep_Objetivos_Cobranza"

    fechaInicial = datetime(dateSelected.year, dateSelected.month ,1)
    fechaInicial_form = fechaInicial.strftime("%Y-%m-%d")

    c.callproc(proc_almacenado_spy_obj, (bytAgencia, bytSucursal, fechaInicial_form, dateSelected))

    capacidad_instalada = c.fetchall()

    c.callproc(proc_almacenado_spy_obj_cobr, (bytAgencia, bytSucursal, fechaInicial_form, dateSelected))

    eficiencia_cobranza = c.fetchall()

    c.close()
    conn.close()

    # DataFrame Capacidad Instalada
    df_cap_instalada = pd.DataFrame.from_records(capacidad_instalada)

    df_cap_instalada.columns = ['Tipo_Cargo', 'Descripcion', 'Objetivo', 'Importe']

    new_row = pd.Series({
        'Tipo_Cargo':0, 
        'Descripcion':'TOTAL', 
        'Objetivo': df_cap_instalada['Objetivo'].sum(), 
        'Importe': df_cap_instalada['Importe'].sum()
    })

    df_cap_instalada.to_dict()

    df_cap_instalada.loc[len(df_cap_instalada)] = new_row

    df_cap_instalada['porcentaje'] = df_cap_instalada.apply(lambda row: (row['Importe'] / row['Objetivo']) * 100 if row['Objetivo'] != 0 else 0, axis=1)

    df_cap_instalada['porcentaje'] = pd.to_numeric(df_cap_instalada['porcentaje'], errors='coerce').round()

    # DataFrame Eficiencia de Cobranza
    df_efi_cobranza = pd.DataFrame.from_records(eficiencia_cobranza)

    df_efi_cobranza.columns = ['Descripcion', 'Objetivo', 'Importe']

    df_efi_cobranza['porcentaje'] = df_efi_cobranza.apply(lambda row: (row['Importe'] / row['Objetivo']) * 100 if row['Objetivo'] != 0 else 0, axis=1)

    df_efi_cobranza['porcentaje'] = pd.to_numeric(df_efi_cobranza['porcentaje'], errors='coerce').round()

    return df_cap_instalada, df_efi_cobranza

    

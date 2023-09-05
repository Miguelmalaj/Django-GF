
from dashboards.utilerias import config
from datetime import datetime, date, timedelta
import pandas as pd
from  .utils import calcula_porcentaje_valor

cadillac = 7    # Constante para la empresa cadillac

def obtener_ventaservicio(bytAgencia, bytSucursal, mes, periodo):
    """
    Obtiene la informacion de venta de servicio, porcentajes de utilidad de mo, tot y totales de servicio
    ademas de obtener el tktpromedio por tipo de orden y por asesor.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strSQL = "SELECT (VS.NOMBRE) AS ASESOR,   (VS.TIOR_DESCRIPCION) as Concepto,  ( 1 )  as Cant,  "
    strSQL = strSQL + " nvl((VS.FASE_REFACCIONES - VS.FASE_DESCUENTOREFACCIONES),0) AS VtaRef, nvl((VS.FASE_COSTOREFACCIONES),0) AS CtoRef, "
    strSQL = strSQL + " nvl((VS.FASE_MANOOBRAMECANICO - VS.FASE_DESCUENTOMECANICO),0) as VtaMO, nvl((VS.FASE_COSTOMECANICO),0) as CtoMO,  "
    strSQL = strSQL + " nvl((VS.FASE_TOTS - VS.FASE_DESCUENTOTOTS + VS.FASE_MATERIALDIVERSO),0) as VtaTOT, nvl((VS.FASE_COSTOTOTS),0) as CtoTOT "
    strSQL = strSQL + " FROM SE_VFACTURASERVICIOS VS "
    strSQL = strSQL + " WHERE VS.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND VS.AGEN_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND (Extract(Month from VS.FASE_FECHA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(Year from VS.FASE_FECHA)) =  " + str(periodo)
    strSQL = strSQL + " UNION ALL "
    strSQL = strSQL + " SELECT (VS.NOMBRE) AS ASESOR,   (VS.TIOR_DESCRIPCION) as Concepto,  ( -1 )  as Cant,  "
    strSQL = strSQL + " nvl((VS.FASE_REFACCIONES - VS.FASE_DESCUENTOREFACCIONES) * -1, 0) AS VtaRef, nvl((VS.FASE_COSTOREFACCIONES) * -1, 0) AS CtoRef, "
    strSQL = strSQL + " nvl((VS.FASE_MANOOBRAMECANICO - VS.FASE_DESCUENTOMECANICO) * -1, 0) as VtaMO, nvl((VS.FASE_COSTOMECANICO) * -1, 0) as CtoMO,  "
    strSQL = strSQL + " nvl((VS.FASE_TOTS - VS.FASE_DESCUENTOTOTS + VS.FASE_MATERIALDIVERSO) * -1, 0) as VtaTOT, nvl((VS.FASE_COSTOTOTS) * -1, 0) as CtoTOT "
    strSQL = strSQL + " FROM SE_VFACTURASERVICIOS VS "
    strSQL = strSQL + " WHERE VS.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND VS.AGEN_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND (Extract(Month from VS.FASE_FECHACANCELACION)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(Year from VS.FASE_FECHACANCELACION)) =  " + str(periodo)

    c.execute(strSQL) 
    df = pd.DataFrame.from_records(c)
    df.columns =["asesor", "concepto", "cant", "vtaref", "ctoref", "vtamo", "ctomo", "vtatot", "ctotot"]

    # Filtrar y calcular utilidades
    filtro_interna = df["concepto"].str.contains("INTERNA", case=False)
    df_utilidad_vtamo_ctomo = df[~filtro_interna].copy()
    df_utilidad_vtamo_ctomo["util"] = df_utilidad_vtamo_ctomo["vtamo"].sum() - df_utilidad_vtamo_ctomo["ctomo"].sum()
    df_utilidad_vtamo_ctomo["porc"] =  (df_utilidad_vtamo_ctomo["util"] / df_utilidad_vtamo_ctomo["vtamo"].sum()) * 100

    df_utilidad_vtatot_ctotot = df[~filtro_interna].copy()
    df_utilidad_vtatot_ctotot["util"] = df_utilidad_vtatot_ctotot["vtatot"].sum() - df_utilidad_vtatot_ctotot["ctotot"].sum()
    df_utilidad_vtatot_ctotot["porc"] = (df_utilidad_vtatot_ctotot["util"] / df_utilidad_vtatot_ctotot["vtatot"].sum()) * 100

    df_utilidad_interna = df[filtro_interna].copy()
    df_utilidad_interna["util"] = (df_utilidad_interna["vtamo"].sum() + df_utilidad_interna["vtatot"].sum()) - (df_utilidad_interna["ctomo"].sum() + df_utilidad_interna["ctotot"].sum())
    df_utilidad_interna["porc"] = (df_utilidad_interna["util"] / (df_utilidad_interna["vtamo"].sum() + df_utilidad_interna["vtatot"].sum())) * 100

    df_utilidad_neta = df.copy()
    df_utilidad_neta["util"] = (df_utilidad_neta["vtamo"].sum() + df_utilidad_neta["vtatot"].sum()) - (df_utilidad_neta["ctomo"].sum() + df_utilidad_neta["ctotot"].sum())
    df_utilidad_neta["porc"] = (df_utilidad_neta["util"] / (df_utilidad_neta["vtamo"].sum() + df_utilidad_neta["vtatot"].sum())) * 100

    # Filtrar conceptos que no contengan "INTERNA" en el concepto
    df_concepto_excluido = df[~df['concepto'].str.contains('INTERNA')]

    # 1. Agrupar por concepto y calcular las sumas de las columnas VTAMO, CTOMO y porcentaje de utilidad
    df_agrupado_vtamo = df_concepto_excluido.groupby('concepto').agg({
        'vtamo': 'sum',
        'ctomo': 'sum',
        'concepto': 'first'
    })
    df_agrupado_vtamo['utilidad'] = df_agrupado_vtamo['vtamo'] - df_agrupado_vtamo['ctomo']
    df_agrupado_vtamo['porc'] = (df_agrupado_vtamo['utilidad'] / df_agrupado_vtamo['vtamo']) * 100
    # Ordenar los datos por utilidad descendente
    df_agrupado_vtamo = df_agrupado_vtamo.sort_values(by='utilidad', ascending=False)

    df_agrupado_vtamo.loc['Suma'] = df_agrupado_vtamo.sum()  # Agregar el renglón de suma
    df_agrupado_vtamo.loc['Suma', 'concepto'] = 'TOTAL'  # Cambiar el valor de concepto en el renglón de suma
    df_agrupado_vtamo['utilidad'] = df_agrupado_vtamo['vtamo'] - df_agrupado_vtamo['ctomo']
    df_agrupado_vtamo['porc'] = (df_agrupado_vtamo['utilidad'] / df_agrupado_vtamo['vtamo']) * 100

    # 2. Agrupar por concepto y calcular las sumas de las columnas VTATOT, CTOTOT y porcentaje de utilidad
    df_agrupado_vtatot = df_concepto_excluido.groupby('concepto').agg({
        'vtatot': 'sum',
        'ctotot': 'sum',
        'concepto': 'first'
    })
    df_agrupado_vtatot['utilidad'] = df_agrupado_vtatot['vtatot'] - df_agrupado_vtatot['ctotot']
    df_agrupado_vtatot['porc'] = (df_agrupado_vtatot['utilidad'] / df_agrupado_vtatot['vtatot']) * 100
     # Ordenar los datos por utilidad descendente
    df_agrupado_vtatot = df_agrupado_vtatot.sort_values(by='utilidad', ascending=False)

    df_agrupado_vtatot.loc['Suma'] = df_agrupado_vtatot.sum()  # Agregar el renglón de suma
    df_agrupado_vtatot.loc['Suma', 'concepto'] = 'TOTAL'  # Cambiar el valor de concepto en el renglón de suma
    df_agrupado_vtatot['utilidad'] = df_agrupado_vtatot['vtatot'] - df_agrupado_vtatot['ctotot']
    df_agrupado_vtatot['porc'] = (df_agrupado_vtatot['utilidad'] / df_agrupado_vtatot['vtatot']) * 100

    # 3. Filtrar conceptos que contengan "INTERNA" en el concepto
    df_concepto_interna = df[df['concepto'].str.contains('INTERNA')]
    df_agrupado_interna = df_concepto_interna.groupby('concepto').agg({
        'vtatot': 'sum',
        'ctotot': 'sum',
        'vtamo': 'sum',
        'ctomo': 'sum',
        'concepto': 'first'
    })

    # Calcular la venta como VTAMO + VTATOT y la utilidad como (VTAMO + VTATOT) - (CTOMO + CTOTOT)
    df_agrupado_interna['venta'] = df_agrupado_interna['vtamo'] + df_agrupado_interna['vtatot']
    df_agrupado_interna['costo'] = df_agrupado_interna['ctomo'] + df_agrupado_interna['ctotot']
    df_agrupado_interna['utilidad'] = df_agrupado_interna['venta'] - df_agrupado_interna['costo']
    df_agrupado_interna['porc'] = (df_agrupado_interna['utilidad'] / df_agrupado_interna['venta']) * 100

    # Ordenar los datos por utilidad descendente
    df_agrupado_interna = df_agrupado_interna.sort_values(by='utilidad', ascending=False)

    df_agrupado_interna.loc['Suma'] = df_agrupado_interna.sum()  # Agregar el renglón de suma
    df_agrupado_interna.loc['Suma', 'concepto'] = 'TOTAL'  # Cambiar el valor de concepto en el renglón de suma
    df_agrupado_interna['utilidad'] = df_agrupado_interna['venta'] - df_agrupado_interna['costo']
    df_agrupado_interna['porc'] = (df_agrupado_interna['utilidad'] / df_agrupado_interna['venta']) * 100
    
    # 4. Agrupar por concepto y calcular ticket promedio por orden de servicio
    df_agrupado_tkpromorden = df_concepto_excluido.groupby('concepto').agg({
        'cant':'sum',
        'vtaref': 'sum',
        'ctoref': 'sum',
        'vtamo': 'sum',
        'ctomo': 'sum',
        'vtatot': 'sum',
        'ctotot': 'sum',
        'concepto': 'first'
    })
    df_agrupado_tkpromorden['utilrefa'] = df_agrupado_tkpromorden['vtaref'] - df_agrupado_tkpromorden['ctoref']
    df_agrupado_tkpromorden['porcrefa'] = (df_agrupado_tkpromorden['utilrefa'] / df_agrupado_tkpromorden['vtaref']) * 100

    df_agrupado_tkpromorden['ventaser'] = (df_agrupado_tkpromorden['vtamo'] + df_agrupado_tkpromorden['vtatot'])
    df_agrupado_tkpromorden['utilserv'] = (df_agrupado_tkpromorden['vtamo'] + df_agrupado_tkpromorden['vtatot']) - (df_agrupado_tkpromorden['ctomo']+ df_agrupado_tkpromorden['ctotot'])
    df_agrupado_tkpromorden['porcserv'] = (df_agrupado_tkpromorden['utilrefa'] / df_agrupado_tkpromorden['vtaref']) * 100
    # Venta, Utilidad y porcentaje total
    df_agrupado_tkpromorden['ventaneta'] = df_agrupado_tkpromorden['vtaref'] + df_agrupado_tkpromorden['vtamo'] + df_agrupado_tkpromorden['vtatot']
    df_agrupado_tkpromorden['costoneta'] = df_agrupado_tkpromorden['ctoref'] + df_agrupado_tkpromorden['ctomo'] + df_agrupado_tkpromorden['ctotot']
    df_agrupado_tkpromorden['utilneta'] = df_agrupado_tkpromorden['ventaneta'] - df_agrupado_tkpromorden['costoneta']
    df_agrupado_tkpromorden['porcneta'] = (df_agrupado_tkpromorden['utilneta'] / df_agrupado_tkpromorden['ventaneta']) * 100
    # TktPromedio
    df_agrupado_tkpromorden['tktorden'] = (df_agrupado_tkpromorden['ventaneta'] / df_agrupado_tkpromorden['cant'])
    # Ordenar los datos por cantidad de ordenes descendente
    df_agrupado_tkpromorden = df_agrupado_tkpromorden.sort_values(by='cant', ascending=False)

    # Calcular los totales directamente en el DataFrame original
    df_total = df_concepto_excluido.sum(numeric_only=True)

    # Calcular utilidades y porcentajes para los totales
    df_total['concepto'] = "TOTAL"
    df_total['ventaref'] = df_total['vtaref']
    df_total['utilrefa'] = df_total['ventaref'] - df_total['ctoref']
    df_total['porcrefa'] = (df_total['utilrefa'] / df_total['ventaref']) * 100
    df_total['ventaser'] = df_total['vtamo'] + df_total['vtatot']
    df_total['utilserv'] = df_total['ventaser'] - (df_total['ctomo'] + df_total['ctotot'])
    df_total['porcserv'] = (df_total['utilserv'] / df_total['ventaser']) * 100

    df_total['ventaneta'] = df_total['vtaref'] + df_total['vtamo'] + df_total['vtatot']
    df_total['costoneta'] = df_total['ctoref'] + df_total['ctomo'] + df_total['ctotot']
    df_total['utilneta'] = df_total['ventaneta'] - df_total['costoneta']
    df_total['porcneta'] = (df_total['utilneta'] / df_total['ventaneta']) * 100
    df_total['tktorden'] = df_total['ventaneta'] / df_total['cant']

    # Agregar una fila "Total" al DataFrame
    df_total = df_total.to_frame().T
    df_total.index = ['Total']  # Cambiar el índice a "Total"

    # 5. Agrupar por concepto y calcular ticket promedio por asesor
    # Filtrar y calcular utilidades
    filtro = df["concepto"].str.contains("PUBLICA", case=False)
    df_ordenes_publico = df[filtro].copy()
    df_agrupado_tktasesor = df_ordenes_publico.groupby('asesor').agg({
        'cant':'sum',
        'vtaref': 'sum',
        'ctoref': 'sum',
        'vtamo': 'sum',
        'ctomo': 'sum',
        'vtatot': 'sum',
        'ctotot': 'sum',
        'asesor': 'first'
    })
    df_agrupado_tktasesor['utilrefa'] = df_agrupado_tktasesor['vtaref'] - df_agrupado_tktasesor['ctoref']
    df_agrupado_tktasesor['porcrefa'] = (df_agrupado_tktasesor['utilrefa'] / df_agrupado_tktasesor['vtaref']) * 100

    df_agrupado_tktasesor['ventaser'] = (df_agrupado_tktasesor['vtamo'] + df_agrupado_tktasesor['vtatot'])
    df_agrupado_tktasesor['utilserv'] = (df_agrupado_tktasesor['vtamo'] + df_agrupado_tktasesor['vtatot']) - (df_agrupado_tktasesor['ctomo']+ df_agrupado_tktasesor['ctotot'])
    df_agrupado_tktasesor['porcserv'] = (df_agrupado_tktasesor['utilrefa'] / df_agrupado_tktasesor['vtaref']) * 100
    # Venta, Utilidad y porcentaje total
    df_agrupado_tktasesor['ventaneta'] = df_agrupado_tktasesor['vtaref'] + df_agrupado_tktasesor['vtamo'] + df_agrupado_tktasesor['vtatot']
    df_agrupado_tktasesor['costoneta'] = df_agrupado_tktasesor['ctoref'] + df_agrupado_tktasesor['ctomo'] + df_agrupado_tktasesor['ctotot']
    df_agrupado_tktasesor['utilneta'] = df_agrupado_tktasesor['ventaneta'] - df_agrupado_tktasesor['costoneta']
    df_agrupado_tktasesor['porcneta'] = (df_agrupado_tktasesor['utilneta'] / df_agrupado_tktasesor['ventaneta']) * 100
    # TktPromedio
    df_agrupado_tktasesor['tktorden'] = (df_agrupado_tktasesor['ventaneta'] / df_agrupado_tktasesor['cant'])
    # Ordenar los datos por cantidad de ordenes descendente
    df_agrupado_tktasesor = df_agrupado_tktasesor.sort_values(by='cant', ascending=False)

    # Calcular los totales directamente en el DataFrame original
    df_totalasesor = df_ordenes_publico.sum(numeric_only=True)

    # Calcular utilidades y porcentajes para los totales
    df_totalasesor['concepto'] = "TOTAL"
    df_totalasesor['ventaref'] = df_totalasesor['vtaref']
    df_totalasesor['utilrefa'] = df_totalasesor['ventaref'] - df_totalasesor['ctoref']
    df_totalasesor['porcrefa'] = (df_totalasesor['utilrefa'] / df_totalasesor['ventaref']) * 100
    df_totalasesor['ventaser'] = df_totalasesor['vtamo'] + df_totalasesor['vtatot']
    df_totalasesor['utilserv'] = df_totalasesor['ventaser'] - (df_totalasesor['ctomo'] + df_totalasesor['ctotot'])
    df_totalasesor['porcserv'] = (df_totalasesor['utilserv'] / df_totalasesor['ventaser']) * 100

    df_totalasesor['ventaneta'] = df_totalasesor['vtaref'] + df_totalasesor['vtamo'] + df_totalasesor['vtatot']
    df_totalasesor['costoneta'] = df_totalasesor['ctoref'] + df_totalasesor['ctomo'] + df_totalasesor['ctotot']
    df_totalasesor['utilneta'] = df_totalasesor['ventaneta'] - df_totalasesor['costoneta']
    df_totalasesor['porcneta'] = (df_totalasesor['utilneta'] / df_totalasesor['ventaneta']) * 100
    df_totalasesor['tktorden'] = df_totalasesor['ventaneta'] / df_totalasesor['cant']

    # Agregar una fila "Total" al DataFrame
    df_totalasesor = df_totalasesor.to_frame().T
    df_totalasesor.index = ['Total']  # Cambiar el índice a "Total"

    return df_utilidad_vtamo_ctomo, df_utilidad_vtatot_ctotot, df_utilidad_interna, df_utilidad_neta, df_agrupado_vtamo, df_agrupado_vtatot, df_agrupado_interna, df_agrupado_tkpromorden, df_agrupado_tktasesor, df_total, df_totalasesor

def agrega_utilidadporcentaje (df_totales):
    """
    Agrega las columnas de utilidad y porcentaje a las tablas de ordenes en proceso
    el dataframe debe tener las columnas de venta y costo vtaref, 'ctoref', 'vtatot', vtamo, ctomo,
        'ctotot', 'vtaneta', 'ctoneto': 
    """

    df_totales['utilneta'] = df_totales['vtaneta'] - df_totales['ctoneto']
    df_totales['porcneto'] = df_totales.apply(lambda row: calcula_porcentaje_valor(row['utilneta'], row['vtaneta']), axis=1)

    df_totales['utilref'] = df_totales['vtaref'] - df_totales['ctoref']
    df_totales['porcref'] = df_totales.apply(lambda row: calcula_porcentaje_valor(row['utilref'], row['vtaref']), axis=1)

    df_totales['utilmo'] = df_totales['vtamo'] - df_totales['ctomo']
    df_totales['porcmo'] = df_totales.apply(lambda row: calcula_porcentaje_valor(row['utilmo'], row['vtamo']), axis=1)

    df_totales['utiltot'] = df_totales['vtatot'] - df_totales['ctotot']
    df_totales['porctot'] = df_totales.apply(lambda row: calcula_porcentaje_valor(row['utiltot'], row['vtatot']), axis=1)
    return df_totales

def obtener_ordenesproceso(bytAgencia, bytSucursal):
    """
    Obtiene la informacion de venta de servicio, porcentajes de utilidad de mo, tot y totales de servicio
    ademas de obtener el tktpromedio por tipo de orden y por asesor.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strSQL = "SELECT  (T.TIOR_DESCRIPCION) as Concepto , (O.ORSE_ESTATUS) as status, (1) as cant,  nvl(O.ORSE_MATERIALDIVERSO, 0) AS vtadiv, nvl((O.ORSE_TOTALMANOOBRA - O.ORSE_DESCUENTOMANOOBRA), 0) as vtamo, "
    strSQL = strSQL + " nvl(O.ORSE_COSTOMANOOBRA, 0) as ctomo, nvl((O.ORSE_TOTALREFACCIONES - O.ORSE_DESCUENTOREFACCIONES), 0) as vtaref, nvl(O.ORSE_COSTOREFACCIONES, 0) as ctoref, "
    strSQL = strSQL + " nvl((O.ORSE_TOTALTOTS - O.ORSE_DESCUENTOTOTS), 0) AS vtatot, nvl(O.ORSE_COSTOTOTS, 0) as ctotot, "
    strSQL = strSQL + " nvl(((O.ORSE_MATERIALDIVERSO + O.ORSE_TOTALMANOOBRA + O.ORSE_TOTALREFACCIONES + O.ORSE_TOTALTOTS) - (O.orse_descuentomanoobra + O.ORSE_DESCUENTOREFACCIONES + O.ORSE_DESCUENTOTOTS )), 0) as vtaneta, "
    strSQL = strSQL + " nvl((O.ORSE_COSTOMANOOBRA + O.ORSE_COSTOREFACCIONES + O.ORSE_COSTOTOTS ), 0) as ctoneto "
    strSQL = strSQL + " FROM SE_ORDENSERVICIO O, SE_TIPOORDEN T "
    strSQL = strSQL + " WHERE O.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND O.ORSE_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND O.ORSE_ESTATUS NOT IN ('FA', 'CA') "
    strSQL = strSQL + " AND T.EMPR_EMPRESAID = O.EMPR_EMPRESAID "
    strSQL = strSQL + " AND T.TIOR_CLAVE = O.ORSE_TIOR_CLAVE "
    c.execute(strSQL) 
    df = pd.DataFrame.from_records(c)
    df.columns =["concepto", "status", "cant", "vtadiv", "vtamo", "ctomo", "vtaref", "ctoref", "vtatot", "ctotot", "vtaneta", "ctoneto"]

    # DataFrame con totales
    df_totales = pd.DataFrame({
        'concepto': ['OR.PROCESO'],
        'status': [''],
        'cant':[df['cant'].sum()],
        'vtadiv': [0.0],
        'vtamo': [df['vtamo'].sum()],
        'ctomo': [df['ctomo'].sum()],
        'vtaref': [df['vtaref'].sum()],
        'ctoref': [df['ctoref'].sum()],
        'vtatot': [df['vtatot'].sum()],
        'ctotot': [df['ctotot'].sum()],
        'vtaneta': [df['vtaneta'].sum()],
        'ctoneto': [df['ctoneto'].sum()]
    })
    df_totales = agrega_utilidadporcentaje(df_totales)
    
    # DataFrame agrupado por status
    df_status = df.groupby('status', as_index=False).sum()
    df_status = agrega_utilidadporcentaje(df_status)
    # Mapa de reemplazo de nombres de status
    status_mapping = {
        'CE': 'CERRADA',
        'ES': 'ESPERA',
        'PR': 'PROCESO'
    }
    # Reemplazar los nombres de status en df_status
    df_status['status'] = df_status['status'].replace(status_mapping)
    df_status = df_status.sort_values(by='cant', ascending=False, ignore_index=True)
    
    # DataFrame agrupado por concepto
    df_concepto = df.groupby('concepto', as_index=False).sum()
    df_concepto = agrega_utilidadporcentaje(df_concepto)
    df_concepto = df_concepto.sort_values(by='cant', ascending=False, ignore_index=True)

    return df_totales, df_status, df_concepto

def obtiene_detalle_ordenes_facturadas(agencia, sucursal, concepto, periodo, mes, tipoconsulta):

    bytempresa = 1
    if agencia == cadillac:
        bytempresa = 2

    conn = None
    conn = config.creaconeccion(agencia)
    c = conn.cursor()

    if tipoconsulta != 3:
        strSQL = " SELECT O.ORSE_FOLIO, O.TIOR_CLAVE, T.TIOR_DESCRIPCION, TO_DATE(ORSE_FECHAENTRADA, 'DD/MM/YY'), ( to_char( SYSDATE - ORSE_FECHAENTRADA, '999' )) AS DIAS "
        strSQL = strSQL + " , (FASE_RAZONSOCIAL) AS ORSE_RAZONSOCIALCLIENTE, nvl(ORSE_CLAVEMODELO,'NO ASIGNADO') AS ORSE_CLAVEMODELO, NVL(ORSE_NUMEROSERIE, ' ') AS ORSE_NUMEROSERIE,  nvl( ( to_char( SYSDATE - ORSE_FECHACIERRE, '999' )), 0) AS DIAS_Cerrada "
        strSQL = strSQL + " , nvl(( to_char( ORSE_FECHACIERRE - ORSE_FECHAENTRADA, '999' )),0) AS DIAS_Taller  "
        strSQL = strSQL + " , sum(O.FASE_MATERIALDIVERSO) AS VtaDiv, nvl(Sum(O.FASE_MANOOBRAMECANICO - O.FASE_DESCUENTOMECANICO) ,0) as VtaMO "
        strSQL = strSQL + " , sum( O.FASE_COSTOMECANICO) as CtoMO, nvl(Sum(O.FASE_REFACCIONES - O.FASE_DESCUENTOREFACCIONES),0) as VtaRef, nvl(Sum(O.FASE_COSTOREFACCIONES),0) AS CtoRef "
        strSQL = strSQL + " , nvl(Sum(O.FASE_TOTS - O.FASE_DESCUENTOTOTS + O.FASE_MATERIALDIVERSO),0) as VtaTOT, nvl(Sum(O.FASE_COSTOTOTS),0) as CtoTOT "
        strSQL = strSQL + " , Sum((O.FASE_MATERIALDIVERSO + O.FASE_MANOOBRAMECANICO + O.FASE_REFACCIONES + O.FASE_TOTS) - (O.FASE_DESCUENTOMECANICO + O.FASE_DESCUENTOREFACCIONES + O.FASE_DESCUENTOTOTS )) as VtaTotal "
        strSQL = strSQL + " , Sum(O.FASE_COSTOMECANICO + O.FASE_COSTOREFACCIONES + O.FASE_COSTOTOTS ) as CtoTotal,  NVL(ORSE_COMENTARIOS, ' ') AS ORSE_COMENTARIOS, O.Nombre, O.FASE_FECHA "
        strSQL = strSQL + " FROM SE_VFACTURASERVICIOS O, SE_TIPOORDEN T "
        strSQL = strSQL + " WHERE O.EMPR_EMPRESAID = " + str(bytempresa)
        strSQL = strSQL + " AND O.AGEN_IDAGENCIA = " + str(sucursal)
        strSQL = strSQL + " AND (Extract(Month from O.FASE_FECHA)) = " + str(mes)
        strSQL = strSQL + " AND (Extract(Year from O.FASE_FECHA)) = " + str(periodo)	
        if tipoconsulta == 1:
            strSQL = strSQL + " AND T.TIOR_DESCRIPCION = '" + str(concepto) + "'"
        else:
            strSQL = strSQL + " AND O.NOMBRE = '" + str(concepto) + "'"
        strSQL = strSQL + " AND T.EMPR_EMPRESAID = O.EMPR_EMPRESAID "
        strSQL = strSQL + " AND T.TIOR_CLAVE = O.TIOR_CLAVE "
        strSQL = strSQL + " Group by  O.ORSE_FOLIO, O.TIOR_CLAVE, ORSE_FECHAENTRADA, ORSE_FECHACIERRE "
        strSQL = strSQL + " , FASE_RAZONSOCIAL, ORSE_CLAVEMODELO, ORSE_NUMEROSERIE, ORSE_COMENTARIOS, T.TIOR_DESCRIPCION, O.Nombre, O.FASE_FECHA "
        strSQL = strSQL + " UNION ALL "
        strSQL = strSQL + " SELECT O.ORSE_FOLIO, O.TIOR_CLAVE, T.TIOR_DESCRIPCION, TO_DATE(ORSE_FECHAENTRADA, 'DD/MM/YY'), ( to_char( SYSDATE - ORSE_FECHAENTRADA, '999' )) AS DIAS "
        strSQL = strSQL + " , (FASE_RAZONSOCIAL) AS ORSE_RAZONSOCIALCLIENTE, nvl(ORSE_CLAVEMODELO,'NO ASIGNADO') AS ORSE_CLAVEMODELO, NVL(ORSE_NUMEROSERIE, ' ') AS ORSE_NUMEROSERIE,  nvl( ( to_char( SYSDATE - ORSE_FECHACIERRE, '999' )), 0) AS DIAS_Cerrada "
        strSQL = strSQL + " , nvl(( to_char( ORSE_FECHACIERRE - ORSE_FECHAENTRADA, '999' )),0) AS DIAS_Taller  "
        strSQL = strSQL + " , sum(O.FASE_MATERIALDIVERSO  * -1) AS VtaDiv, nvl(Sum(O.FASE_MANOOBRAMECANICO - O.FASE_DESCUENTOMECANICO) * -1 ,0) as VtaMO "
        strSQL = strSQL + " , sum( O.FASE_COSTOMECANICO  * -1) as CtoMO, nvl(Sum(O.FASE_REFACCIONES - O.FASE_DESCUENTOREFACCIONES)  * -1,0) as VtaRef, nvl(Sum(O.FASE_COSTOREFACCIONES)  * -1,0) AS CtoRef "
        strSQL = strSQL + " , nvl(Sum(O.FASE_TOTS - O.FASE_DESCUENTOTOTS + O.FASE_MATERIALDIVERSO)  * -1,0) as VtaTOT, nvl(Sum(O.FASE_COSTOTOTS)  * -1,0) as CtoTOT "
        strSQL = strSQL + " , Sum((O.FASE_MATERIALDIVERSO + O.FASE_MANOOBRAMECANICO + O.FASE_REFACCIONES + O.FASE_TOTS) - (O.FASE_DESCUENTOMECANICO + O.FASE_DESCUENTOREFACCIONES + O.FASE_DESCUENTOTOTS ) ) * -1 as VtaTotal "
        strSQL = strSQL + " , Sum(O.FASE_COSTOMECANICO + O.FASE_COSTOREFACCIONES + O.FASE_COSTOTOTS )  * -1 as CtoTotal,  NVL(ORSE_COMENTARIOS, ' ') AS ORSE_COMENTARIOS, O.Nombre, O.FASE_FECHACANCELACION "
        strSQL = strSQL + " FROM SE_VFACTURASERVICIOS O, SE_TIPOORDEN T "
        strSQL = strSQL + " WHERE O.EMPR_EMPRESAID = " + str(bytempresa)
        strSQL = strSQL + " AND O.AGEN_IDAGENCIA = " + str(sucursal)
        strSQL = strSQL + " AND (Extract(Month from O.FASE_FECHACANCELACION)) = " + str(mes)
        strSQL = strSQL + " AND (Extract(Year from O.FASE_FECHACANCELACION)) = " + str(periodo)	
        if tipoconsulta == 1:
            strSQL = strSQL + " AND T.TIOR_DESCRIPCION = '" + str(concepto) + "'"
        else:
            strSQL = strSQL + " AND O.NOMBRE = '" + str(concepto) + "'"
        strSQL = strSQL + " AND T.EMPR_EMPRESAID = O.EMPR_EMPRESAID "
        strSQL = strSQL + " AND T.TIOR_CLAVE = O.TIOR_CLAVE "
        strSQL = strSQL + " Group by  O.ORSE_FOLIO, O.TIOR_CLAVE, ORSE_FECHAENTRADA, ORSE_FECHACIERRE "
        strSQL = strSQL + " , FASE_RAZONSOCIAL, ORSE_CLAVEMODELO, ORSE_NUMEROSERIE, ORSE_COMENTARIOS, T.TIOR_DESCRIPCION, O.Nombre, O.FASE_FECHACANCELACION "
        strSQL = strSQL + " ORDER BY DIAS DESC "
    else:
        # Obtiene el detalle de las ordenes de servicio dependiendo del Tipo de status
        strSQL = " SELECT O.ORSE_FOLIO, ORSE_TIOR_CLAVE, T.TIOR_DESCRIPCION, TO_DATE(ORSE_FECHAENTRADA, 'DD/MM/YY'), ( to_char( SYSDATE - ORSE_FECHAENTRADA, '999' )) AS DIAS "
        strSQL = strSQL + " , ORSE_RAZONSOCIALCLIENTE, nvl(ORSE_CLAVEMODELO,'NO ASIGNADO') AS ORSE_CLAVEMODELO, NVL(ORSE_NUMEROSERIE, ' ') AS ORSE_NUMEROSERIE,  nvl( ( to_char( SYSDATE - ORSE_FECHACIERRE, '999' )), 0) AS DIAS_Cerrada "
        strSQL = strSQL + " , NVL(( to_char( ORSE_FECHACIERRE - ORSE_FECHAENTRADA, '999' )),0) AS DIAS_Taller  "
        strSQL = strSQL + " , SUM(O.ORSE_MATERIALDIVERSO) AS VtaDiv, Sum(O.ORSE_TOTALMANOOBRA - O.ORSE_DESCUENTOMANOOBRA) as VtaMO "
        strSQL = strSQL + " , SUM( O.ORSE_COSTOMANOOBRA) as CtoMO, Sum(O.ORSE_TOTALREFACCIONES - O.ORSE_DESCUENTOREFACCIONES ) as VtaRef, Sum( O.ORSE_COSTOREFACCIONES ) as CtoRef "
        strSQL = strSQL + " , SUM( O.ORSE_TOTALTOTS - O.ORSE_DESCUENTOTOTS ) AS VtaTOT, Sum( O.ORSE_COSTOTOTS ) as CtoTOT "
        strSQL = strSQL + " , SUM((O.ORSE_MATERIALDIVERSO + O.ORSE_TOTALMANOOBRA + O.ORSE_TOTALREFACCIONES + O.ORSE_TOTALTOTS) - (O.orse_descuentomanoobra + O.ORSE_DESCUENTOREFACCIONES + O.ORSE_DESCUENTOTOTS )) as VtaTotal "
        strSQL = strSQL + " , SUM(O.ORSE_COSTOMANOOBRA + O.ORSE_COSTOREFACCIONES + O.ORSE_COSTOTOTS ) as CtoTotal,  NVL(ORSE_COMENTARIOS, ' ') AS ORSE_COMENTARIOS, (E.EMPL_NOMBRE) as Asesor, TO_DATE('01/01/1900', 'DD/MM/YY')"
        strSQL = strSQL + " FROM SE_ORDENSERVICIO O, SE_TIPOORDEN T, EMPLEADOS E "
        strSQL = strSQL + " WHERE O.EMPR_EMPRESAID = " + str(bytempresa)
        strSQL = strSQL + " AND O.ORSE_IDAGENCIA = " + str(sucursal)
        strSQL = strSQL + " AND O.ORSE_ESTATUS NOT IN ('FA', 'CA') "
        strSQL = strSQL + " AND ORSE_ESTATUS = '" + str(concepto[:2]) + "'" #Obtener los primeros dos caracteres del estatus de la orden [PR, CE, ES]
        strSQL = strSQL + " AND T.EMPR_EMPRESAID = O.EMPR_EMPRESAID "
        strSQL = strSQL + " AND T.TIOR_CLAVE = O.ORSE_TIOR_CLAVE "
        strSQL = strSQL + " AND E.EMPR_EMPRESAID = O.EMPR_EMPRESAID "
        strSQL = strSQL + " AND E.EMPL_CLAVE = O.ORSE_EMPL_CLAVE "
        strSQL = strSQL + " Group by  O.ORSE_FOLIO, ORSE_TIOR_CLAVE, ORSE_FECHAENTRADA, ORSE_FECHACIERRE, "
        strSQL = strSQL + " ORSE_RAZONSOCIALCLIENTE, ORSE_CLAVEMODELO, ORSE_NUMEROSERIE, ORSE_COMENTARIOS, T.TIOR_DESCRIPCION, E.EMPL_NOMBRE "
        strSQL = strSQL + " ORDER BY DIAS DESC "
        
    c.execute(str(strSQL)) 

    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns =['orden', 'clave', 'tipoorden', 'fentrada', 'dias', 'cliente', 'modelo', 'vin', 'dcerrada', 'dtaller', 'vdiv', 'vmo', 'cmo', 'vref', 'cref','vtot', 'ctot', 'vneta', 'cneto', 'coment', 'asesor', 'fecha']
    # Convierte las columnas al tipo datetime
    df_consulta['fentrada'] = pd.to_datetime(df_consulta['fentrada'])
    df_consulta['fecha'] = pd.to_datetime(df_consulta['fecha'])
    # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
    df_consulta[['fentrada', 'fecha']] = df_consulta[['fentrada', 'fecha']].applymap(lambda x: x.strftime('%d/%m/%y'))
    # Limitar el numero de caracteres por columna
    df_consulta['cliente'] = df_consulta['cliente'].str[:30]
    df_consulta['vin'] = df_consulta['vin'].str[-8:]
    df_consulta['utilneta'] = df_consulta['vneta'] - df_consulta['cneto']
    df_consulta['porcneto'] = df_consulta.apply(lambda row: calcula_porcentaje_valor(row['utilneta'], row['vneta']), axis=1)

    df_consulta['utilref'] = df_consulta['vref'] - df_consulta['cref']
    df_consulta['porcref'] = df_consulta.apply(lambda row: calcula_porcentaje_valor(row['utilref'], row['vref']), axis=1)

    df_consulta['utilmo'] = df_consulta['vmo'] - df_consulta['cmo']
    df_consulta['porcmo'] = df_consulta.apply(lambda row: calcula_porcentaje_valor(row['utilmo'], row['vmo']), axis=1)

    df_consulta['utiltot'] = df_consulta['vtot'] - df_consulta['ctot']
    df_consulta['porctot'] = df_consulta.apply(lambda row: calcula_porcentaje_valor(row['utiltot'], row['vtot']), axis=1)
    
    return df_consulta

def obtener_resumen_ventarefacciones(bytAgencia, bytSucursal, mes, periodo):
    """
    Obtiene la informacion de venta de refacciones, porcentajes de utilidad y detalles por area
    ademas de obtener el tktpromedio por asesor.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strSQL = " SELECT TO_DATE(PEDI_FECHAFACTURA, 'DD/MM/YY') AS FECHA, PEDI_NUMEROFACTURA, PEDI_RAZONFACTURA, PROD_CLAVE, PROD_DESCRIPCION1, CANTIDAD, PRECIO, COSTO, UTILIDAD, "
    strSQL = strSQL + " TIPO_DESCRIPCION, TIPOCTES_DESCRIPCION, DEPTO, CANALVTA "
    strSQL = strSQL + " FROM RE_VCBOANALISISMOSTRADOR  "	
    strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND PEDI_ALMA_CLAVE = " + str(bytSucursal)
    strSQL = strSQL + " AND Depto IN (' REFACCIONES', ' SERVICIO') "
    # strSQL = strSQL + " AND CanalVta = 'VENTA MOSTRADOR' "
    strSQL = strSQL + " AND (Extract(Month from PEDI_FECHAFACTURA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(Year from PEDI_FECHAFACTURA)) = " + str(periodo)
    strSQL = strSQL + " Order by PEDI_FECHAFACTURA Desc "

    c.execute(strSQL) 
    df = pd.DataFrame.from_records(c)
    df.columns =["fecha", "factura", "cliente", "codigo", "articulo", "cant", "venta", "costo", "utilidad", "grupo", "tipovta", "depto", "canalvta" ]

    # Filtrar los datos por departamentos y tipos de venta
    df_refacciones = df[df['depto'] == ' REFACCIONES']
    df_servicio_externo = df[(df['depto'] == ' SERVICIO') & (~df['tipovta'].str.contains('INTERNA'))]
    df_servicio_interno = df[(df['depto'] == ' SERVICIO') & (df['tipovta'].str.contains('INTERNA'))]

    # 1. Suma total de la venta y utilidad en REFACCIONES
    vtaref = df_refacciones['venta'].sum()
    utilref = df_refacciones['utilidad'].sum()
    porcref = calcula_porcentaje_valor(utilref, vtaref)

    # 2. Suma total de la venta y utilidad en SERVICIO (excluyendo INTERNA)
    vtaser = df_servicio_externo['venta'].sum()
    utilser = df_servicio_externo['utilidad'].sum()
    porcser = calcula_porcentaje_valor(utilser, vtaser)

    # 3. Suma total de la venta y utilidad en SERVICIO (INTERNA)
    vtainterna = df_servicio_interno['venta'].sum()
    utilinterna = df_servicio_interno['utilidad'].sum()
    porcinterna = calcula_porcentaje_valor(utilinterna, vtainterna)

    # 4. Suma total de la venta y utilidad en todo el DataFrame
    ventatotal = df['venta'].sum()
    utiltotal = df['utilidad'].sum()
    porctotal = calcula_porcentaje_valor(utiltotal, ventatotal)

    return utilref, porcref, utilser, porcser, utilinterna, porcinterna, ventatotal, utiltotal, porctotal

def obtener_ventarefacciones(bytAgencia, bytSucursal, mes, periodo):
    """
    Obtiene la informacion de venta de refacciones, porcentajes de utilidad y detalles por area
    ademas de obtener el tktpromedio por asesor.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strSQL = " SELECT TO_DATE(PEDI_FECHAFACTURA, 'DD/MM/YY') AS FECHA, PEDI_NUMEROFACTURA, PEDI_RAZONFACTURA, PROD_CLAVE, PROD_DESCRIPCION1, CANTIDAD, PRECIO, COSTO, UTILIDAD, "
    strSQL = strSQL + " TIPO_DESCRIPCION, TIPOCTES_DESCRIPCION, DEPTO, CANALVTA, EMPLEADO "
    strSQL = strSQL + " FROM RE_VCBOANALISISMOSTRADOR  "	
    strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND PEDI_ALMA_CLAVE = " + str(bytSucursal)
    strSQL = strSQL + " AND Depto IN (' REFACCIONES', ' SERVICIO') "
    # strSQL = strSQL + " AND CanalVta = 'VENTA MOSTRADOR' "
    strSQL = strSQL + " AND (Extract(Month from PEDI_FECHAFACTURA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(Year from PEDI_FECHAFACTURA)) = " + str(periodo)
    strSQL = strSQL + " Order by PEDI_FECHAFACTURA Desc "

    c.execute(strSQL) 
    df = pd.DataFrame.from_records(c)
    df.columns =["fecha", "factura", "cliente", "codigo", "articulo", "cant", "venta", "costo", "utilidad", "grupo", "tipovta", "depto", "canalvta", "empleado" ]

    # Filtrar los datos por departamentos y tipos de venta
    df_refacciones = df[df['depto'] == ' REFACCIONES']
    df_servicio_externo = df[(df['depto'] == ' SERVICIO') & (~df['tipovta'].str.contains('INTERNA'))]
    df_servicio_interno = df[(df['depto'] == ' SERVICIO') & (df['tipovta'].str.contains('INTERNA'))]

    # 1. Suma de la venta y utilidad por tipovta en REFACCIONES
    df_refacciones_tipovta = df_refacciones.groupby('tipovta').agg({
        'venta':'sum',
        'utilidad': 'sum',
        'tipovta': 'first'
    })
    df_refacciones_tipovta['porc'] = (df_refacciones_tipovta['utilidad'] / df_refacciones_tipovta['venta']) * 100
    df_refacciones_tipovta = df_refacciones_tipovta.sort_values(by='venta', ascending=False)

    # Agregar los totales
    df_refacciones_tipovta.loc['Suma'] = df_refacciones_tipovta.sum()  # Agregar el renglón de suma
    df_refacciones_tipovta.loc['Suma', 'tipovta'] = 'TOTAL'  # Cambiar el valor de concepto en el renglón de suma
    df_refacciones_tipovta['porc'] = (df_refacciones_tipovta['utilidad'] / df_refacciones_tipovta['venta']) * 100


    # 2. Suma de la venta y utilidad por tipovta en SERVICIO (excluyendo INTERNA)
    df_servicio_externo_tipovta = df_servicio_externo.groupby('tipovta').agg({'venta': 'sum', 'utilidad': 'sum', 'tipovta':'first'})
    df_servicio_externo_tipovta['porc'] = (df_servicio_externo_tipovta['utilidad'] / df_servicio_externo_tipovta['venta']) * 100
    df_servicio_externo_tipovta = df_servicio_externo_tipovta.sort_values(by='venta', ascending=False)
    # Agregar los totales
    df_servicio_externo_tipovta.loc['Suma'] = df_servicio_externo_tipovta.sum()  # Agregar el renglón de suma
    df_servicio_externo_tipovta.loc['Suma', 'tipovta'] = 'TOTAL'  # Cambiar el valor de concepto en el renglón de suma
    df_servicio_externo_tipovta['porc'] = (df_servicio_externo_tipovta['utilidad'] / df_servicio_externo_tipovta['venta']) * 100

    # 3. Suma de la venta y utilidad por tipovta en SERVICIO (INTERNA)
    df_servicio_interno_tipovta = df_servicio_interno.groupby('tipovta').agg({'venta': 'sum', 'utilidad': 'sum', 'tipovta':'first'})
    df_servicio_interno_tipovta = df_servicio_interno_tipovta.sort_values(by='venta', ascending=False)
    # Agregar los totales
    df_servicio_interno_tipovta.loc['Suma'] = df_servicio_interno_tipovta.sum()  # Agregar el renglón de suma
    df_servicio_interno_tipovta.loc['Suma', 'tipovta'] = 'TOTAL'  # Cambiar el valor de concepto en el renglón de suma
    df_servicio_interno_tipovta['porc'] = (df_servicio_interno_tipovta['utilidad'] / df_servicio_interno_tipovta['venta']) * 100

    # 4. Suma de la venta y utilidad por empleado en REFACCIONES y VENTA MOSTRADOR
    df_refacciones_ventamostrador = df_refacciones[(df_refacciones['canalvta'] == 'VENTA MOSTRADOR') & (df_refacciones['empleado'].str.contains('!'))]
    df_refacciones_ventamostrador_empleado = df_refacciones_ventamostrador.groupby('empleado').agg({'venta': 'sum', 'utilidad': 'sum', 'empleado':'first'})
    df_refacciones_ventamostrador_empleado = df_refacciones_ventamostrador_empleado.sort_values(by='venta', ascending=False)
    # Agregar los totales
    df_refacciones_ventamostrador_empleado.loc['Suma'] = df_refacciones_ventamostrador_empleado.sum()  # Agregar el renglón de suma
    df_refacciones_ventamostrador_empleado.loc['Suma', 'empleado'] = 'TOTAL'  # Cambiar el valor de concepto en el renglón de suma
    df_refacciones_ventamostrador_empleado['porc'] = (df_refacciones_ventamostrador_empleado['utilidad'] / df_refacciones_ventamostrador_empleado['venta']) * 100

    # df_refacciones_final = df_refacciones_ventamostrador_empleado['empleado'].str.contains('*')

    return df_refacciones_tipovta, df_servicio_externo_tipovta, df_servicio_interno_tipovta, df_refacciones_ventamostrador_empleado

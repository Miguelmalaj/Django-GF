
from dashboards.utilerias import config, consultassql, utilerias
from datetime import datetime, date, timedelta
import pandas as pd

cadillac = 7    # Constante para la empresa cadillac

def ventas_anuales (bytAgencia, bytSucursal, periodo):
    df_vehiculosbaja = ventas_x_vehiculo_mes(bytAgencia, bytSucursal, periodo)
    df_vendedores = ventas_x_vend_mes(bytAgencia, bytSucursal, periodo)
    return df_vehiculosbaja,  df_vendedores

def entregas_anuales (bytAgencia, bytSucursal, periodo):
    df_vehiculos = entregas_x_unidad_mes(bytAgencia, bytSucursal, periodo)
    df_vendedores = entregas_x_vendedor_mes(bytAgencia, bytSucursal, periodo)
    return df_vehiculos, df_vendedores
    
def ventas_x_vehiculo_mes(bytAgencia, bytSucursal, periodo):
    """
    Obtiene las ventas por Tipo de Vehiculo y las regresa en una tabla pivote.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    dic_gamabaja = {'AVEO', 'ONIX', 'CAVALIER', 'GROOVE', 'TRACKER', 'TRAX', 'CAPTIVA', 'TORNADO', 'S10', 'XT4', 'XT5', 'MONTANA'}

    #Obtener las Ventas por vehiculos. y agruparlas en la tabla temporal
    strSQL = " SELECT nvl((Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ),'*** N/E ***') as Concepto, "
    strSQL += " nvl((SUM(1)),0) as Cant, Extract(Month from FAAU_FECHA) as mes "
    strSQL += " FROM AUTOS.VT_VLIBRODEVENTAS " 
    strSQL += " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL += " AND (Extract(Month from FAAU_FECHA)) >= 1 " 
    strSQL += " AND (Extract(Month from FAAU_FECHA)) <= 12 "  
    strSQL += " AND (Extract(year from FAAU_FECHA)) = " + str(periodo)
    strSQL += " AND VEHI_CLASE = 'NU'"
    strSQL += " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:
        strSQL += " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL += " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL += " AND AGEN_IDAGENCIA = 1 "
        strSQL += " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL += " GROUP BY MODE_BASICO, Extract(Month from FAAU_FECHA) "
    strSQL += " UNION ALL "
    strSQL += " SELECT nvl((Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ),'*** N/E ***') as Concepto, "
    strSQL += " nvl((SUM(-1)),0) as Cant, Extract(Month from FAAU_FECHACANCELACION) as mes "
    strSQL += " FROM AUTOS.VT_VLIBRODEVENTAS " 
    strSQL += " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL += " AND (Extract(Month from FAAU_FECHACANCELACION)) >=  1 "
    strSQL += " AND (Extract(Month from FAAU_FECHACANCELACION)) <=  12 "
    strSQL += " AND (Extract(year from FAAU_FECHACANCELACION)) = " + str(periodo)
    strSQL += " AND VEHI_CLASE = 'NU'"
    strSQL += " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:
        strSQL += " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL += " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL += " AND AGEN_IDAGENCIA = 1 "
        strSQL += " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL += " GROUP BY MODE_BASICO, Extract(Month from FAAU_FECHACANCELACION) "

    c.execute(str(strSQL)) 

    # Crear el DataFrame obtenido de la consulta
    df_consulta = pd.DataFrame.from_records(c)
    # Cerramos la coneccion a la BD
    conn.close()

    # Asignar los nombres de las columnas
    df_consulta.columns= ['vehiculo', 'cantidad', 'mes']

    # Crear la tabla pivote, por el tipo de vehiculo, para que los agrupe.
    tmp_df = df_consulta[['vehiculo', 'cantidad', 'mes']].copy()
    pivot_table = tmp_df.pivot_table(
    index=['vehiculo'],
    columns=['mes'],
    values=['cantidad'],
    aggfunc={'cantidad': ['sum']}
    ).fillna(0)

    df = completar_columnas(pivot_table) # Acompletar los meses que faltan para los 12
    lista_datos = df.reset_index().to_dict()  # Pasar la tabla pivote a un diccionario de datos para eliminar el formato de tabla pivote y quedarnos con los datos planos.
    df_pivot = pd.DataFrame.from_dict(lista_datos)   # Volver a crear el DataFrame del diccionario de datos.

    df_pivot.columns=['vehiculo','ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'] # Asignar los nombres a las columnas 
    
    # Crear una columna "gama" basada en los diccionarios de gama
    df_pivot['gama'] = df_pivot['vehiculo'].apply(lambda x: 'baja' if x in dic_gamabaja else 'alta')

    # Re ordenar las columnas, para que la columna Baja nos quede despues del vehiculo
    df_columns = [col for col in df_pivot.columns if col != 'gama']
    df_columns.insert(1, 'gama')
    df_pivot = df_pivot[df_columns]

    # Asignar el indice de la tabla.
    df_detallevehiculos = df_pivot.set_index('vehiculo')

    # Ahora separamos los dataframes por tipo de gama.
    df_gamabaja = df_detallevehiculos[df_detallevehiculos['gama'] == 'baja']
    df_gamaalta = df_detallevehiculos[df_detallevehiculos['gama'] == 'alta']

    # Eliminar las columnas que no necesitamos
    df_gamabaja.drop(['gama'], axis=1, inplace=True)
    df_gamaalta.drop(['gama'], axis=1, inplace=True)

    # # Calcular el total por registro
    df_gamabaja['Total Registro'] = df_gamabaja.sum(axis=1)
    df_gamaalta['Total Registro'] = df_gamaalta.sum(axis=1)

    # Calcular los subtotales por gama
    subtotales_gama = df_detallevehiculos.groupby('gama').sum().fillna({'gama':'-'})

    # # Calcular el total por registro
    df_temp = subtotales_gama.rename(index={'alta':'SUBTOT ALTA', 'baja':'SUBTOT BAJA'})
    df_gamas = agregar_totales(df_temp, 'TOTAL VENTAS')

     # Calcular el total general por cada mes
    total_general_mes = subtotales_gama.sum(axis=0)
    # Calcular el porcentaje de cada gama respecto al total de registros por cada mes
    porcentajes_gama = subtotales_gama.div(total_general_mes, axis=1) * 100
    df_porcertanje = porcentajes_gama.rename(index={'alta':'% ALTA', 'baja':'% BAJA'})

    df_concatenado = pd.concat([df_gamas, df_porcertanje], axis=0)

    df_temp = df_concatenado.sort_values('Total Registro', ascending=False).fillna("-")

    # Obtener filas con etiquetas 
    df_totalgral = df_temp.loc[['TOTAL VENTAS']]
    df_subtbaja = df_temp.loc[['SUBTOT BAJA']]
    df_porcbaja = df_temp.loc[['% BAJA']]
    df_subtalta = df_temp.loc[['SUBTOT ALTA']]
    df_porcalta = df_temp.loc[['% ALTA']]

    df_ordenado = pd.concat([df_totalgral, df_gamabaja, df_subtbaja, df_porcbaja, df_gamaalta, df_subtalta, df_porcalta ], axis=0)

    return df_ordenado

def ventas_x_vend_mes(bytAgencia, bytSucursal, periodo):
    """
    Obtiene las ventas por Vendedor y las regresa en una tabla pivote.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    # LIMPIAR LA TABLA TEMPORAL DE RESULTADOS
    strSQL = "DELETE FROM AUTOS.VT_RESULTADOS "
    c.execute (strSQL) 

    #Obtener las Ventas por vehiculos. y agruparlas en la tabla temporal
    strSQL = "INSERT INTO AUTOS.VT_RESULTADOS( Concepto, Cant, Total ) "
    strSQL = strSQL + " SELECT nvl(SUBSTR(NOMVENDEDOR, 1,25),'*** N/E ***') as Concepto,  nvl((SUM(1)),0) as Cant, Extract(Month from FAAU_FECHA) as mes "
    strSQL = strSQL + " FROM AUTOS.VT_VLIBRODEVENTAS " 
    strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHA)) >= 1 " 
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHA)) <= 12 "  
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHA)) = " + str(periodo)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " GROUP BY SUBSTR(NOMVENDEDOR, 1,25), Extract(Month from FAAU_FECHA) "
    strSQL = strSQL + " UNION ALL "
    strSQL = strSQL + " SELECT nvl(SUBSTR(NOMVENDEDOR, 1,25),'*** N/E ***') as Concepto,  nvl((SUM(-1)),0) as Cant, Extract(Month from FAAU_FECHACANCELACION) as mes "
    strSQL = strSQL + " FROM AUTOS.VT_VLIBRODEVENTAS " 
    strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHACANCELACION)) >=  1 "
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHACANCELACION)) <=  12 "
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHACANCELACION)) = " + str(periodo)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " GROUP BY SUBSTR(NOMVENDEDOR, 1,25), Extract(Month from FAAU_FECHACANCELACION) "

    c.execute(str(strSQL)) 
    # Obtener el resultado de la tabla temporal
    strSQL = "SELECT Concepto, (Sum(Cant)) as Cant, (Total) as Total "
    strSQL = strSQL + " From AUTOS.VT_RESULTADOS "
    strSQL = strSQL + " Group by Concepto, total "
    strSQL = strSQL + " Order by Concepto, Total, Cant Desc " 
    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)

    # Crear la tabla pivot en un nuevo DataFrame
    df=df_consulta.pivot(index=0, columns=2, values=1).fillna(0)

    df_pivot = completar_columnas(df)
    df_pivot = agregar_totales(df_pivot)

    df_pivot = df_pivot.sort_values(by='Total Registro', ascending=False)
    conn.close()
    return df_pivot

def entregas_x_vendedor_mes(bytAgencia, bytSucursal, periodo):
    """
    Obtiene las entregas por vendedor y las regresa en una tabla pivote.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    # LIMPIAR LA TABLA TEMPORAL DE RESULTADOS
    strSQL = "DELETE FROM AUTOS.VT_RESULTADOS "
    c.execute (strSQL) 

    #Obtener las Ventas por vehiculos. y agruparlas en la tabla temporal
    strSQL = "INSERT INTO AUTOS.VT_RESULTADOS( Concepto, Cant, Total ) "
    strSQL = strSQL + " SELECT nvl(V.NOMVENDEDOR,'*** N/E ***') as Concepto,  nvl((SUM(1)),0) as Cant, Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD) as Mes "
    strSQL = strSQL + " From GM_ENTREGAUNIDAD  ET, VT_VLIBRODEVENTAS V "
    strSQL = strSQL + " Where ET.empr_empresaid = " + str(bytEmpresa)
    strSQL = strSQL + " AND ET.AGEN_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND ET.ENTR_STATUS = 'AC' "
    strSQL = strSQL + " and ET.ENTR_VEHI_CLASE = 'NU' "
    strSQL = strSQL + " AND (Extract(year from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo)
    strSQL = strSQL + " AND ET.empr_empresaid = v.Empr_empresaid "
    strSQL = strSQL + " AND ET.ENTR_FAAU_NOFACTURA = V.FAAU_NOFACTURA "
    strSQL = strSQL + " AND V.PEAU_TIPOVENTA <> 'INTERCAMB' "
    strSQL = strSQL + " Group by V.NOMVENDEDOR, Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD)"
    
    c.execute(str(strSQL)) 
    # Obtener el resultado de la tabla temporal
    strSQL = "SELECT Concepto, (Sum(Cant)) as Cant, (Total) as Total "
    strSQL = strSQL + " From AUTOS.VT_RESULTADOS "
    strSQL = strSQL + " Group by Concepto, total "
    strSQL = strSQL + " Order by Concepto, Total, Cant Desc " 
    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consultaentrega = pd.DataFrame.from_records(c)

    # Crear la tabla pivot en un nuevo DataFrame
    df=df_consultaentrega.pivot(index=0, columns=2, values=1).fillna(0)

    df_pivot = completar_columnas(df)
    conn.close()
    return df_pivot

def entregas_x_unidad_mes(bytAgencia, bytSucursal, periodo):
    """
    Obtiene las entregas por Tipo de Vehiculo y las regresa en una tabla pivote.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    # LIMPIAR LA TABLA TEMPORAL DE RESULTADOS
    strSQL = "DELETE FROM AUTOS.VT_RESULTADOS "
    c.execute (strSQL) 

    #Obtener las Ventas por vehiculos. y agruparlas en la tabla temporal
    strSQL = "INSERT INTO AUTOS.VT_RESULTADOS( Concepto, Cant, Total ) "
    strSQL = strSQL + " SELECT nvl(V.MODE_BASICO,'*** N/E ***') as Concepto,  nvl((SUM(1)),0) as Cant, Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD) as Mes "
    strSQL = strSQL + " From GM_ENTREGAUNIDAD  ET, VT_VLIBRODEVENTAS V "
    strSQL = strSQL + " Where ET.empr_empresaid = " + str(bytEmpresa)
    strSQL = strSQL + " AND ET.AGEN_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND ET.ENTR_STATUS = 'AC' "
    strSQL = strSQL + " and ET.ENTR_VEHI_CLASE = 'NU' "
    strSQL = strSQL + " AND (Extract(year from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo)
    strSQL = strSQL + " AND ET.empr_empresaid = v.Empr_empresaid "
    strSQL = strSQL + " AND ET.ENTR_FAAU_NOFACTURA = V.FAAU_NOFACTURA "
    strSQL = strSQL + " AND V.PEAU_TIPOVENTA <> 'INTERCAMB' "
    strSQL = strSQL + " Group by V.MODE_BASICO, Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD)"
    
    c.execute(str(strSQL)) 
    # Obtener el resultado de la tabla temporal
    strSQL = "SELECT Concepto, (Sum(Cant)) as Cant, (Total) as Total "
    strSQL = strSQL + " From AUTOS.VT_RESULTADOS "
    strSQL = strSQL + " Group by Concepto, total "
    strSQL = strSQL + " Order by Concepto, Total, Cant Desc " 
    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consultaentrega = pd.DataFrame.from_records(c)

    # Crear la tabla pivot en un nuevo DataFrame
    df=df_consultaentrega.pivot(index=0, columns=2, values=1).fillna(0)

    df_pivot = completar_columnas(df)
    conn.close()
    return df_pivot

def obtiene_ventasvehiculos(bytAgencia, bytSucursal, fechareporte):
    """
    Obtiene la informacion de vehiculos, ventas, entregas, cancelaciones y unidades
    facturadas no entregadas 
    """
    strFechaini = fechareporte
    periodo = fechareporte

    
    strFechaFin = strFechaini + timedelta(days=1)
    strFechaFin = strFechaFin.strftime("%d/%m/%Y")
    strFechaini = strFechaini.strftime("%d/%m/%Y")

    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    # Ventas en el Dia
    strSQL = "SELECT  VT.VEHI_CLASE as CLASE, "
    strSQL = strSQL + " ( CASE WHEN  Extract(day from VT.FAAU_FECHAREPORTE) = " + str(periodo.day) + " THEN FAAU_CONTADORFACTURA ELSE 0 END ) as HOY, "
    strSQL = strSQL + " nvl(( FAAU_CONTADORFACTURA ),0) as ACUMULADO, "
    strSQL = strSQL + " nvl(( CASE WHEN FAAU_STATUS = 'CA' THEN ( CASE WHEN  Extract(Month from VT.FAAU_FECHA) = " + str(periodo.month) + " THEN 0 ELSE 1 END ) ELSE 0 END ), 0) as CANCELADAS, "
    strSQL = strSQL + " nvl(FAU_Venta, 0) as venta "
    strSQL = strSQL + " From VT_VLIBRODEVENTASCAN VT "
    strSQL = strSQL + " WHERE vt.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from vt.FAAU_FECHAREPORTE)) = " + str(periodo.month) 
    strSQL = strSQL + " AND (Extract(year from vt.FAAU_FECHAREPORTE)) = " + str(periodo.year) 
    strSQL = strSQL + " AND vt.PEAU_TIPOVENTA <> 'INTERCAMB' "
    if bytSucursal != 3:
        strSQL = strSQL + " AND VT.AGEN_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND VT.PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND VT.AGEN_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND VT.PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " UNION ALL"
    strSQL = strSQL + " SELECT 'NU' AS CLASE, (0) AS HOY, (0) AS ACUMULADO, (0) AS CANCELADAS, (0) AS VENTAS FROM DUAL"

    c.execute(str(strSQL)) 

    df = pd.DataFrame.from_records(c)

    #Agregar las Entregas del mes 
    strSQL = " Select  'ENTREGAS' AS CONCEPTO, COUNT(FAAU_NOFACTURA), nvl(sum(FAAU_TOTAL), 0) "
    strSQL = strSQL + " From GM_VADMINENTREGAS  ET "
    strSQL = strSQL + " Where ET.empr_empresaid =  " + str(bytEmpresa)
    strSQL = strSQL + " AND ET.ENTR_STATUS = 'AC' "
    strSQL = strSQL + " and ET.ENTR_VEHI_CLASE = 'NU' "
    strSQL = strSQL + " AND NVL(ET.ENTR_SOFIACODE, ' ') <> ' ' "
    strSQL = strSQL + " AND (Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo.month)
    strSQL = strSQL + " AND (Extract(year from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo.year)
    strSQL = strSQL + " AND FAAU_FORM_TIPOVENTA not like '%INTER%' "
    if bytSucursal != 3:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND ET.FAAU_FORM_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND ET.FAAU_FORM_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " UNION ALL "   #Agregar las FNE
    strSQL = strSQL + " SELECT  'FNE' as concepto, count(v.vehi_numeroinventario), nvl(sum(VT.FAAU_TOTAL),0) as venta"
    strSQL = strSQL + " FROM vt_vinventarioautos V , VT_FACTURAAUTOS VT, VT_VENDEDORES VD, VT_PRIMPLANPISO PP, GM_VADMINENTREGAS ET  "
    strSQL = strSQL + " WHERE V.empr_empresaid = " + str(bytEmpresa)
    strSQL = strSQL + " and V.VEHI_STATUS = 'FA' "
    strSQL = strSQL + " and V.VEHI_CLASE = 'NU' "
    strSQL = strSQL + " And V.VEHI_CLASE = VT.FAAU_VEHI_CLASE "
    strSQL = strSQL + " And V.VEHI_ANIO = VT.FAAU_VEHI_ANIO "
    strSQL = strSQL + " And V.VEHI_NUMEROINVENTARIO = VT.FAAU_VEHI_NUMEROINVENTARIO "
    strSQL = strSQL + " And VT.FAAU_STATUS = 'AC' "
    strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA NOT LIKE ('INTER%') "
    strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA NOT LIKE ('DEMO%') "
    strSQL = strSQL + " And VD.Empr_Empresaid = vt.Empr_empresaid "
    strSQL = strSQL + " and vd.vend_clave = vt.faau_vend_clave "
    strSQL = strSQL + " And V.EMPR_EMPRESAID = pp.empr_empresaid "
    strSQL = strSQL + " And V.VEHI_CLASE = pp.PRIM_VEHI_CLASE "
    strSQL = strSQL + " And V.vehi_anio = pp.prim_vehi_anio "		
    strSQL = strSQL + " And V.vehi_numeroinventario = PP.prim_VEHI_NUMEROINVENTARIO "
    strSQL = strSQL + " And Abs(pp.Prim_Saldo) > 1 "
    if bytSucursal != 3:
        strSQL = strSQL + " AND VD.VEND_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA not like ('FLOT%') "
    else:
        strSQL = strSQL + " AND VD.VEND_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA like ('FLOT%') "
    strSQL = strSQL + " AND ET.EMPR_EMPRESAID = VT.EMPR_EMPRESAID "
    strSQL = strSQL + " AND ET.FAAU_NOFACTURA = VT.FAAU_NOFACTURA"
    strSQL = strSQL + " AND NVL(ET.ENTR_FECHAENTREGAUNIDAD, TO_DATE('01/01/1900', 'DD/MM/YYYY')) = TO_DATE('01/01/1900', 'DD/MM/YYYY') "

    c.execute(str(strSQL)) 

    df_consulta = pd.DataFrame.from_records(c)
    conn.close()  

    # Procesar la consulta de las ventas para tomar las ventas de hoy, acumuladas y canceladas.
    df.columns =['Clase', 'Hoy', 'Acumulado', 'Canceladas', 'Venta']

    df_consulta.reset_index()
    df_consulta.columns = ['concepto', 'cant', 'venta']
    df_entregas = df_consulta.set_index('concepto')

    # Filtrar por la clase "NU"
    df_nu = df[df['Clase'] == 'NU']
    # Filtrar por la clase "US"
    df_us = df[df['Clase'] == 'US']

    # DataFrame nuevo para la clase "NU"
    df_nu_nuevo = pd.DataFrame({
        'concepto': ['HOY', 'ACUMULADO', 'TICKETPROM', 'CANCELADAS'],
        'cant': [df_nu['Hoy'].sum(), df_nu['Acumulado'].sum(), 0,  df_nu['Canceladas'].sum()],
        'venta': [df_nu.loc[df_nu['Hoy'] != 0, 'Venta'].sum(), df_nu.loc[df_nu['Acumulado'] !=0 , 'Venta'].sum(), df_nu.loc[df_nu['Acumulado'] !=0 , 'Venta'].sum() / df_nu['Acumulado'].sum() if df_nu['Acumulado'].sum() != 0 else 0, df_nu.loc[df_nu['Canceladas'] != 0, 'Venta'].sum() ]
    })

    # DataFrame nuevo para la clase "US"
    df_us_nuevo = pd.DataFrame({
        'concepto': ['HOY', 'ACUMULADO', 'CANCELADAS'],
        'cant': [df_us['Hoy'].sum(), df_us['Acumulado'].sum(), df_us.loc[df_us['Canceladas'] != 0, 'Canceladas'].sum()],
        'venta': [df_us.loc[df_us['Hoy'] != 0, 'Venta'].sum(), df_us.loc[df_us['Acumulado'] != 0, 'Venta'].sum(), df_us.loc[df_us['Canceladas'] != 0, 'Venta'].sum()]
    })
    df_final_nu = pd.concat([df_nu_nuevo.set_index('concepto'), df_entregas], axis= 0)
    df_final_us = df_us_nuevo.set_index('concepto')

    return df_final_nu, df_final_us

def obtiene_ventasvehiculos_detalle(bytAgencia, bytSucursal, fechareporte):
    """
    Obtiene la informacion de vehiculos, ventas, entregas, cancelaciones y unidades
    facturadas no entregadas 
    """
    strFechaini = fechareporte
    periodo = fechareporte

    
    strFechaFin = strFechaini + timedelta(days=1)
    strFechaFin = strFechaFin.strftime("%d/%m/%Y")
    strFechaini = strFechaini.strftime("%d/%m/%Y")

    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    # Ventas en el Dia
    strSQL = " SELECT Inventario, DescModelo, NVL(FAAU_NOFACTURA, '0') as FAAU_NOFACTURA,  NVL(FAAU_razonfactura, 'X') AS FAAU_razonfactura, "
    strSQL = strSQL + " NVL(PEAU_TipoVenta,'X') AS PEAU_TipoVenta, NVL(Nomvendedor, 'X') AS Nomvendedor, NVL(FAU_Venta, '0') AS FAU_Venta,  (Costooperacion - Bonificacion ) as Costooperacion "
    strSQL =  strSQL + ", (FAU_Venta - (Costooperacion - Bonificacion )) as Utilidad, VT.VEHI_CLASE as CLASE, VT.FAAU_STATUS, VT.FAAU_CONTADORFACTURA, " 
    strSQL = strSQL + " ( CASE WHEN  Extract(day from VT.FAAU_FECHAREPORTE) = " + str(periodo.day) + " THEN 'HOY' ELSE 'ACUM' END ) as HOY_ACUM, " 
    strSQL = strSQL + " nvl((Case When INSTR(DescModelo, ' ') > 0 Then SUBSTR(DescModelo, 1, INSTR(DescModelo, ' ') - 1) else DescModelo end ),'*** N/E ***') as MODE_BASICO, "
    strSQL = strSQL + " nvl(( Case When FAU_Venta <> 0 Then  (FAU_Venta - (Costooperacion - Bonificacion )) / FAU_Venta * 100 else 0 end ) , 0) as porcentaje, "
    strSQL = strSQL + " TO_DATE(FAAU_FECHA, 'DD/MM/YY') as fechafact, TO_DATE(FAAU_FECHACANCELACION, 'DD/MM/YY') as Fechacanc "
    strSQL = strSQL + " From VT_VLIBRODEVENTASCAN VT "
    strSQL = strSQL + " WHERE vt.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from vt.FAAU_FECHAREPORTE)) = " + str(periodo.month) 
    strSQL = strSQL + " AND (Extract(year from vt.FAAU_FECHAREPORTE)) = " + str(periodo.year) 
    strSQL = strSQL + " AND vt.PEAU_TIPOVENTA <> 'INTERCAMB' "
    if bytSucursal != 3:
        strSQL = strSQL + " AND VT.AGEN_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND VT.PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND VT.AGEN_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND VT.PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " UNION ALL"
    strSQL = strSQL + " SELECT '' AS INV, '' AS DESCM, '0' AS FACT, '' AS RAZONF, '' AS TIPOVEN, '' AS VEND, 0 AS VTA, 0 AS CTO, 0 AS UTIL, '' AS CLASE, "
    strSQL = strSQL + " '' AS STATUS, 0 AS CONTA, '' AS HOY, '' AS MODELO, 0 as porce, TO_DATE('', 'DD/MM/YY') as fechafac, TO_DATE('', 'DD/MM/YY') as fechacanc  "
    strSQL = strSQL + " FROM DUAL"

    c.execute(str(strSQL)) 

    df_consulta = pd.DataFrame.from_records(c)
    # Procesar la consulta de las ventas para tomar las ventas de hoy, acumuladas y canceladas.
    df_consulta.columns =['inv', 'descm', 'factura', 'cliente', 'tipoventa', 'vendedor', 'venta', 'costo', 'utilidad', 'clase', 'status', 'contador', 'hoy_acum', 'modebasico', 'porcentaje', 'fecfactura', 'feccancelacion']

    # Obtener los vehiculos nuevos de hoy
    dfn_hoy = df_consulta[['inv', 'descm', 'factura', 'cliente', 'tipoventa', 'vendedor', 'venta', 'costo', 'utilidad', 'clase',  'hoy_acum', 'porcentaje']].copy(deep=True)
    dfn_hoy = dfn_hoy[(dfn_hoy['hoy_acum'] == 'HOY') & (dfn_hoy['clase'] == 'NU')]  #Filtrar por las columnas que necesitamos
    # Eliminar las columnas que no necesitamos
    dfn_hoy.drop(['clase', 'hoy_acum'], axis=1, inplace=True)

    # Obtener los vehiculos usados Acumulados
    dfn_acum = df_consulta[['inv', 'descm', 'factura', 'cliente', 'tipoventa', 'vendedor', 'venta', 'costo', 'utilidad', 'clase',  'hoy_acum', 'porcentaje']].copy(deep=True)
    dfn_acum = dfn_acum[(dfn_acum['hoy_acum'] == 'ACUM') & (dfn_acum['clase'] == 'NU')]  #Filtrar por las columnas que necesitamos
    # Eliminar las columnas que no necesitamos
    dfn_acum.drop(['clase', 'hoy_acum'], axis=1, inplace=True)

    # Obtener los vehiculos nuevos Cancelados
    dfn_cancel = df_consulta[['inv', 'descm', 'factura', 'fecfactura', 'feccancelacion', 'vendedor', 'cliente', 'tipoventa', 'venta', 'costo', 'utilidad', 'porcentaje', 'status', 'clase']].copy(deep=True)
    dfn_cancel = dfn_cancel[(dfn_cancel['status'] == 'CA') & (dfn_cancel['clase'] == 'NU')] #Filtrar por las columnas que necesitamos
    dfn_cancel = dfn_cancel.sort_values(by='fecfactura', ascending=True)
    # Convierte las columnas 'fecfactura' y 'feccancelacion' al tipo datetime
    dfn_cancel['fecfactura'] = pd.to_datetime(dfn_cancel['fecfactura'])
    dfn_cancel['feccancelacion'] = pd.to_datetime(dfn_cancel['feccancelacion'])

    # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
    dfn_cancel[['fecfactura', 'feccancelacion']] = dfn_cancel[['fecfactura', 'feccancelacion']].applymap(lambda x: x.strftime('%d/%m/%y'))

    # Eliminar las columnas que no necesitamos
    dfn_cancel.drop(['clase', 'status'], axis=1, inplace=True)
    
     # Crear las tablas pivote por tipo de vehiculo, vendedor y tipo de venta
    tmp_df = df_consulta[df_consulta['clase'] == 'NU']
    tmp_df = tmp_df[['venta', 'modebasico', 'contador']].copy()
    pivot_table = tmp_df.pivot_table(
        index=['modebasico'],
        values=['contador', 'venta'],
        aggfunc={'contador': ['sum'], 'venta': ['sum']}
    )
    pivot_table.columns=['cant', 'venta']
    lista_datos = pivot_table.reset_index().to_dict() # Pasar la tabla pivote a un diccionario de datos para eliminar el formato de tabla pivote y quedarnos con los datos planos.
    dfn_modebasico = pd.DataFrame.from_dict(lista_datos)   # Volver a crear el DataFrame del diccionario de datos.
    dfn_modebasico = dfn_modebasico.sort_values(by='cant', ascending=False, ignore_index=True)

    tmp_df = df_consulta[df_consulta['clase'] == 'NU']
    tmp_df = tmp_df[['venta', 'vendedor', 'contador']].copy()
    pivot_table = tmp_df.pivot_table(
        index=['vendedor'],
        values=['contador', 'venta'],
        aggfunc={'contador': ['sum'], 'venta': ['sum']}
    )  
    pivot_table.columns=['cant', 'venta']
    lista_datos = pivot_table.reset_index().to_dict() # Pasar la tabla pivote a un diccionario de datos para eliminar el formato de tabla pivote y quedarnos con los datos planos.
    dfn_vendedor = pd.DataFrame.from_dict(lista_datos)   # Volver a crear el DataFrame del diccionario de datos.
    dfn_vendedor = dfn_vendedor.sort_values(by='cant', ascending=False, na_position='last', ignore_index=True)

    tmp_df = df_consulta[df_consulta['clase'] == 'NU']
    tmp_df = tmp_df[['venta', 'tipoventa', 'contador']].copy()
    pivot_table = tmp_df.pivot_table(
        index=['tipoventa'],
        values=['contador', 'venta'],
        aggfunc={'contador': ['sum'], 'venta': ['sum']}
    )
    pivot_table.columns=['cant', 'venta']
    lista_datos = pivot_table.reset_index().to_dict() # Pasar la tabla pivote a un diccionario de datos para eliminar el formato de tabla pivote y quedarnos con los datos planos.
    dfn_tipoventa = pd.DataFrame.from_dict(lista_datos)   # Volver a crear el DataFrame del diccionario de datos.
    dfn_tipoventa = dfn_tipoventa.sort_values(by='cant', ascending=False, na_position='last', ignore_index=True)

    # ******************************************************************
    # Obtener la informacion de los seminuevos
    # ******************************************************************
     # Obtener los vehiculos usados de hoy
    dfu_hoy = df_consulta[['inv', 'descm', 'factura', 'cliente', 'tipoventa', 'vendedor', 'venta', 'costo', 'utilidad', 'clase',  'hoy_acum', 'porcentaje']].copy(deep=True)
    dfu_hoy = dfu_hoy[(dfu_hoy['hoy_acum'] == 'HOY') & (dfu_hoy['clase'] == 'US')]  #Filtrar por las columnas que necesitamos
    # Eliminar las columnas que no necesitamos
    dfu_hoy.drop(['clase', 'hoy_acum'], axis=1, inplace=True)

    # Obtener los vehiculos usados Acumulados
    dfu_acum = df_consulta[['inv', 'descm', 'factura', 'cliente', 'tipoventa', 'vendedor', 'venta', 'costo', 'utilidad', 'clase',  'hoy_acum', 'porcentaje']].copy(deep=True)
    dfu_acum = dfu_acum[(dfu_acum['hoy_acum'] == 'ACUM') & (dfu_acum['clase'] == 'US')]  #Filtrar por las columnas que necesitamos
    # Eliminar las columnas que no necesitamos
    dfu_acum.drop(['clase', 'hoy_acum'], axis=1, inplace=True)

    # Obtener los vehiculos nuevos Cancelados
    dfu_cancel = df_consulta[['inv', 'descm', 'factura', 'fecfactura', 'feccancelacion', 'vendedor', 'cliente', 'tipoventa', 'venta', 'costo', 'utilidad', 'porcentaje', 'status', 'clase']].copy(deep=True)
    dfu_cancel = dfu_cancel[(dfu_cancel['status'] == 'CA') & (dfu_cancel['clase'] == 'US')] #Filtrar por las columnas que necesitamos
    dfu_cancel = dfu_cancel.sort_values(by='fecfactura', ascending=True)
    # Convierte las columnas 'fecfactura' y 'feccancelacion' al tipo datetime
    dfu_cancel['fecfactura'] = pd.to_datetime(dfu_cancel['fecfactura'])
    dfu_cancel['feccancelacion'] = pd.to_datetime(dfu_cancel['feccancelacion'])

    # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
    dfu_cancel[['fecfactura', 'feccancelacion']] = dfu_cancel[['fecfactura', 'feccancelacion']].applymap(lambda x: x.strftime('%d/%m/%y'))

    # Eliminar las columnas que no necesitamos
    dfu_cancel.drop(['clase', 'status'], axis=1, inplace=True)
    
     # Crear las tablas pivote por tipo de vehiculo, vendedor y tipo de venta
    tmp_df = df_consulta[df_consulta['clase'] == 'US']
    tmp_df = tmp_df[['venta', 'modebasico', 'contador']].copy()
    pivot_table = tmp_df.pivot_table(
        index=['modebasico'],
        values=['contador', 'venta'],
        aggfunc={'contador': ['sum'], 'venta': ['sum']}
    )
    if not pivot_table.empty:
        pivot_table.columns=['cant', 'venta']
        lista_datos = pivot_table.reset_index().to_dict() # Pasar la tabla pivote a un diccionario de datos para eliminar el formato de tabla pivote y quedarnos con los datos planos.
        dfu_modebasico = pd.DataFrame.from_dict(lista_datos)   # Volver a crear el DataFrame del diccionario de datos.
        dfu_modebasico = dfu_modebasico.sort_values(by='cant', ascending=False, ignore_index=True)
    else:
        dfu_modebasico = pivot_table

    tmp_df = df_consulta[df_consulta['clase'] == 'US']
    tmp_df = tmp_df[['venta', 'vendedor', 'contador']].copy()
    pivot_table = tmp_df.pivot_table(
        index=['vendedor'],
        values=['contador', 'venta'],
        aggfunc={'contador': ['sum'], 'venta': ['sum']}
    )  
    if not pivot_table.empty:
        pivot_table.columns=['cant', 'venta']
        lista_datos = pivot_table.reset_index().to_dict() # Pasar la tabla pivote a un diccionario de datos para eliminar el formato de tabla pivote y quedarnos con los datos planos.
        dfu_vendedor = pd.DataFrame.from_dict(lista_datos)   # Volver a crear el DataFrame del diccionario de datos.
        dfu_vendedor = dfu_vendedor.sort_values(by='cant', ascending=False, na_position='last', ignore_index=True)
    else:  
        dfu_vendedor = pivot_table

    tmp_df = df_consulta[df_consulta['clase'] == 'US']
    tmp_df = tmp_df[['venta', 'tipoventa', 'contador']].copy()
    pivot_table = tmp_df.pivot_table(
        index=['tipoventa'],
        values=['contador', 'venta'],
        aggfunc={'contador': ['sum'], 'venta': ['sum']}
    )
    if not pivot_table.empty:
        pivot_table.columns=['cant', 'venta']
        lista_datos = pivot_table.reset_index().to_dict() # Pasar la tabla pivote a un diccionario de datos para eliminar el formato de tabla pivote y quedarnos con los datos planos.
        dfu_tipoventa = pd.DataFrame.from_dict(lista_datos)   # Volver a crear el DataFrame del diccionario de datos.
        dfu_tipoventa = dfu_tipoventa.sort_values(by='cant', ascending=False, na_position='last', ignore_index=True)
    else:
        dfu_tipoventa = pivot_table

    # #Agregar las Entregas del mes 
    strSQL = " Select (ENTR_VEHI_CLASE || '-' || ENTR_VEHI_ANIO || '-' ||  ENTR_VEHI_NUMEROINVENTARIO) as Inv, MODE_DESCRIPMODELO,  NVL(FAAU_NOFACTURA, '') as FAAU_NOFACTURA, TO_DATE(FAAU_FECHA) AS FECHAFAC, TO_DATE(ENTR_FECHAENTREGAUNIDAD) AS FECHAENTREGA, NVL(FAAU_razonfactura, '') AS FAAU_razonfactura,  "
    strSQL = strSQL + " NVL(FAAU_FORM_TIPOVENTA,'') AS PEAU_TipoVenta, NVL(vendedor, '') AS Nomvendedor,  NVL(FAAU_TOTAL, '') AS FAU_Venta, (Trunc(Sysdate) - Trunc(ENTR_FECHAENTREGAUNIDAD)) as diasentrega "
    strSQL = strSQL + " From GM_VADMINENTREGAS ET "
    strSQL = strSQL + " Where ET.empr_empresaid =  " + str(bytEmpresa)
    strSQL = strSQL + " AND ET.ENTR_STATUS = 'AC' "
    strSQL = strSQL + " and ET.ENTR_VEHI_CLASE = 'NU' "
    strSQL = strSQL + " AND (Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo.month)
    strSQL = strSQL + " AND (Extract(year from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo.year)
    strSQL = strSQL + " AND FAAU_FORM_TIPOVENTA not like '%INTER%' "
    if bytSucursal != 3:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND ET.FAAU_FORM_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND ET.FAAU_FORM_TIPOVENTA like '%FLOT%'"
   
    
    c.execute(str(strSQL)) 
    conn.close
    df_consulta = pd.DataFrame.from_records(c)
    if not df_consulta.empty:
        # Procesar la consulta de las ventas para tomar las ventas de hoy, acumuladas y canceladas.
        df_consulta.columns =['inv', 'descm', 'factura', 'fecfactura', 'fecentrega', 'cliente', 'tipoventa', 'vendedor', 'venta', 'diasentrega']
        dfn_entregas = df_consulta[['inv', 'descm', 'factura', 'fecfactura', 'fecentrega', 'diasentrega', 'vendedor' ,'cliente', 'tipoventa', 'venta']].copy(deep=True)
        # Convierte las columnas al tipo datetime
        dfn_entregas['fecfactura'] = pd.to_datetime(dfn_entregas['fecfactura'])
        dfn_entregas['fecentrega'] = pd.to_datetime(dfn_entregas['fecentrega'])

        # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
        dfn_entregas[['fecfactura', 'fecentrega']] = dfn_entregas[['fecfactura', 'fecentrega']].applymap(lambda x: x.strftime('%d/%m/%y'))
        dfn_entregas = dfn_entregas.sort_values(by='diasentrega', ascending=False, na_position='last', ignore_index=True)
    else:
        dfn_entregas = df_consulta

    strSQL = "SELECT (PP.PRIM_VEHI_CLASE || '-' || pp.prim_VEHI_ANIO || '-' || PP.PRIM_VEHI_NUMEROINVENTARIO) as INVENTARIO, V.MODE_DESCRIPCION, V.VEHI_SERIE, TO_DATE(V.VEHI_FECHAASIGNACION, 'DD/MM/YY') AS FECHAASIGN, TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY') AS FECHAINTERES, "
    strSQL = strSQL + " (Trunc(Sysdate) - Trunc(TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY'))) as diasPP, (Trunc(Sysdate) - Trunc(TO_DATE(V.VEHI_FECHAVENDIDO, 'DD/MM/YY'))) as dias,  NVL(VT.FAAU_FORM_TIPOVENTA, '') AS PEAU_TIPOVENTA, TO_DATE(V.VEHI_FECHAVENDIDO, 'DD/MM/YY') AS VEHI_FECHAVENDIDO, "
    strSQL = strSQL + " NVL(VT.FAAU_NOFACTURA, '0') as FAAU_NOFACTURA, VT.FAAU_CLIE_CLAVE, NVL(VT.FAAU_RAZONFACTURA, '-') as FAAU_RAZONFACTURA, VT.FAAU_TOTAL, (PA.PEAU_BONIFICACION * 1.16) as PEAU_BONIFICACION,"
    strSQL = strSQL + " (PP.PRIM_SALDO * -1) AS PRIM_SALDO, "
    strSQL = strSQL + " (SELECT  NVL(SUM(PRIM_SALDO),0) AS SALDO "
    strSQL = strSQL + " 			FROM CC_PRIMCLIENTES C "
    strSQL = strSQL + " 			WHERE C.EMPR_EMPRESAID = VT.EMPR_EMPRESAID "
    strSQL = strSQL + " 			AND C.PRIM_DOCUMENTO = VT.FAAU_NOFACTURA "
    strSQL = strSQL + " 			AND C.PRIM_CLIE_CLAVE = VT.FAAU_CLIE_CLAVE) as SALDOCARTERA, "
    strSQL = strSQL + "  NVL(( Select SUM(pb.PRIM_SALDO)  from VT_PRIMBONIF  pb "
    strSQL = strSQL + "  			where pb.empr_empresaid = " + str(bytEmpresa)
    strSQL = strSQL + "  			and PB.PRIM_TIPO_CLAVE = 'POVE' "
    strSQL = strSQL + "  			and PB.PRIM_VEHI_CLASE = PP.PRIM_VEHI_CLASE "
    strSQL = strSQL + "  			and PB.PRIM_VEHI_ANIO = PP.PRIM_VEHI_ANIO "
    strSQL = strSQL + "  			and PB.PRIM_VEHI_NUMEROINVENTARIO = PP.PRIM_VEHI_NUMEROINVENTARIO ), 0 ) as PagoBonif "
    strSQL = strSQL + " FROM vt_primplanpiso pp, vt_vinventarioautos V, VT_FACTURAAUTOS VT, VT_PEDIDOAUTOS PA, GM_VADMINENTREGAS ET, VT_VENDEDORES VD "
    strSQL = strSQL + " WHERE PP.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND Abs(pp.Prim_Saldo) > 1 "
    strSQL = strSQL + " AND V.EMPR_EMPRESAID = pp.EMPR_EMPRESAID "
    strSQL = strSQL + " AND V.vehi_clas_clave = pp.PRIM_VEHI_CLASE"
    strSQL = strSQL + " AND v.vehi_anio = pp.prim_vehi_anio"
    strSQL = strSQL + " AND V.VEHI_STATUS = 'FA' "
    strSQL = strSQL + " AND V.VEHI_NUMEROINVENTARIO = PP.prim_VEHI_NUMEROINVENTARIO "
    strSQL = strSQL + " AND PP.EMPR_EMPRESAID = VT.EMPR_EMPRESAID "
    strSQL = strSQL + " AND PP.PRIM_VEHI_CLASE = VT.FAAU_VEHI_CLASE "
    strSQL = strSQL + " AND PP.prim_VEHI_ANIO = VT.FAAU_VEHI_ANIO "
    strSQL = strSQL + " AND PP.PRIM_VEHI_NUMEROINVENTARIO = VT.FAAU_VEHI_NUMEROINVENTARIO "
    strSQL = strSQL + " AND VT.FAAU_STATUS = 'AC' "
    strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA not like ('INTERC%') "
    strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA NOT LIKE ('DEMO%') "
    strSQL = strSQL + " And VD.Empr_Empresaid = vt.Empr_empresaid "
    strSQL = strSQL + " and vd.vend_clave = vt.faau_vend_clave "
    if bytSucursal != 3:
        strSQL = strSQL + " AND VD.VEND_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA not like ('FLOT%') "
    else:
        strSQL = strSQL + " AND VD.VEND_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND VT.FAAU_FORM_TIPOVENTA like ('FLOT%') "
    strSQL = strSQL + " AND PA.EMPR_EMPRESAID = VT.EMPR_EMPRESAID "
    strSQL = strSQL + " AND PA.PEAU_NUMEROPEDIDO = VT.FAAU_PEAU_NUMEROPEDIDO"
    strSQL = strSQL + " AND ET.EMPR_EMPRESAID = VT.EMPR_EMPRESAID "
    strSQL = strSQL + " AND ET.FAAU_NOFACTURA = VT.FAAU_NOFACTURA"
    strSQL = strSQL + " AND NVL(ET.ENTR_FECHAENTREGAUNIDAD, TO_DATE('01/01/1900', 'DD/MM/YYYY')) = TO_DATE('01/01/1900', 'DD/MM/YYYY') "
    strSQL = strSQL + " ORDER BY diasPP DESC, VT.FAAU_FORM_TIPOVENTA, PP.PRIM_VEHI_CLASE, PP.PRIM_VEHI_ANIO, PP.PRIM_VEHI_NUMEROINVENTARIO "

    c.execute(str(strSQL)) 

    df_consulta = pd.DataFrame.from_records(c)
    conn.close()  

    if not df_consulta.empty:
        # Procesar la consulta de las ventas para tomar las ventas de hoy, acumuladas y canceladas.
        df_consulta.columns =['inv', 'descm', 'vin', 'fasignacion', 'finteres', 'diaspp', 'dias', 'tipoventa', 'fventa', 'factura', 'cliente', 'nomcliente', 'venta', 'bonif', 'saldopp', 'saldocxc', 'saldobonif']
        dfn_fne = df_consulta[['inv', 'descm', 'vin', 'fasignacion', 'finteres', 'diaspp', 'fventa', 'dias', 'tipoventa', 'factura', 'cliente', 'nomcliente', 'venta', 'bonif','saldobonif', 'saldocxc','saldopp']].copy(deep=True)
        # Convierte las columnas al tipo datetime
        dfn_fne['fasignacion'] = pd.to_datetime(dfn_fne['fasignacion'])
        dfn_fne['finteres'] = pd.to_datetime(dfn_fne['finteres'])
        dfn_fne['fventa'] = pd.to_datetime(dfn_fne['fventa'])

        # Limitar el numero de caracteres por columna
        dfn_fne['descm'] = dfn_fne['descm'].str[:20]
        dfn_fne['vin'] = dfn_fne['vin'].str[-8:]

        # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
        dfn_fne[['fasignacion', 'finteres', 'fventa']] = dfn_fne[['fasignacion', 'finteres', 'fventa']].applymap(lambda x: x.strftime('%d/%m/%y'))
        dfn_fne = dfn_fne.sort_values(by='diaspp', ascending=False, na_position='last', ignore_index=True)
    else:
        dfn_fne = df_consulta


    return dfn_hoy, dfn_acum, dfn_cancel, dfn_modebasico, dfn_vendedor, dfn_tipoventa, dfn_entregas, dfn_fne, dfu_hoy, dfu_acum, dfu_cancel, dfu_modebasico, dfu_tipoventa, dfu_vendedor

def obtiene_fact_entregas(bytAgencia, bytSucursal, mes, periodo):
    """
    Obtiene la informacion de vehiculos, ventas, entregas, cancelaciones para el funnel de ventas
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    intVentasAcum = 0
    intCanceladas = 0
    intdemos = 0
    intEntregasGMF = 0
    intEntregasCont = 0

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()
    
    # Ventas Acumuladas del ejercicio actual
    strSQL = "SELECT   nvl(SUM(1), 0) as Cant,  NVL(SUM(FAU_Venta),0) as Total, ('') as tipoVenta FROM VT_VLIBRODEVENTAS "
    strSQL = strSQL + "WHERE EMPR_EMPRESAID =  " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHA)) = " + str(periodo)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:    
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " UNION ALL "   #Agregar las Canceladas 
    strSQL = strSQL + " SELECT  nvl(SUM(1), 0) as Cant,  NVL(SUM(FAU_Venta),0) as Total, ('') as tipoVenta FROM VT_VLIBRODEVENTAS "
    strSQL = strSQL + " WHERE EMPR_EMPRESAID =  " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHACANCELACION)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHACANCELACION)) = " + str(periodo)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:    
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " UNION ALL "   #Agregar las Demos 
    strSQL = strSQL + " SELECT nvl(COUNT (SAAD_FOLIO),0) as Cant, (0) as Total, ('') as tipoVenta from VT_VSALIDAAUTOSDEMO "
    strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND (Extract(Month from FECHAALTA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FECHAALTA)) = " + str(periodo)
    strSQL = strSQL + " AND SAAD_VEHI_CLASE <> 'US' "
    strSQL = strSQL + " UNION ALL "   #Agregar las Entregas del mes 
    strSQL = strSQL + " Select  nvl(COUNT(ET.ENTR_FOLIOENTREGA), 0) AS Entregados, NVL(SUM(FAU_Venta),0) as Total, NVL(V.PEAU_TipoVenta,'') AS PEAU_TipoVenta "
    strSQL = strSQL + " From GM_ENTREGAUNIDAD  ET, VT_VLIBRODEVENTAS V "
    strSQL = strSQL + " Where ET.empr_empresaid =  " + str(bytEmpresa)
    strSQL = strSQL + " AND ET.ENTR_STATUS = 'AC' "
    strSQL = strSQL + " and ET.ENTR_VEHI_CLASE = 'NU' "
    strSQL = strSQL + " AND (Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo)
    strSQL = strSQL + " AND ET.empr_empresaid = v.Empr_empresaid "
    strSQL = strSQL + " AND ET.ENTR_FAAU_NOFACTURA = V.FAAU_NOFACTURA "
    strSQL = strSQL + " AND V.PEAU_TIPOVENTA <> 'INTERCAMB' "
    if bytSucursal != 3:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND V.PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND V.PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " GROUP BY V.PEAU_TipoVenta"

    c.execute(str(strSQL)) 
    numero_registro =0
    
    for row in c:
        numero_registro +=1
        if numero_registro == 1:
            intVentasAcum =  int(row[0])
        elif numero_registro == 2:
            intCanceladas = int(row[0]) 
        elif numero_registro == 3:
            intdemos = int(row[0]) 
        elif numero_registro >= 4:
            if row[2][:3] == 'GMF':
                intEntregasGMF = int(row[0]) 
            else:
                intEntregasCont = intEntregasCont + int(row[0])

    # Ventas Acumuladas del ejercicio anterior
    strSQL = "SELECT   SUM(1) as Cant,  NVL(SUM(FAU_Venta),0) as Total, ('') as tipoVenta FROM VT_VLIBRODEVENTAS "
    strSQL = strSQL + "WHERE EMPR_EMPRESAID =  " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHA)) = " + str(periodo - 1)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:    
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " UNION ALL "   #Agregar las Canceladas 
    strSQL = strSQL + " SELECT  SUM(1) as Cant,  NVL(SUM(FAU_Venta),0) as Total, ('') as tipoVenta FROM VT_VLIBRODEVENTAS "
    strSQL = strSQL + " WHERE EMPR_EMPRESAID =  " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHACANCELACION)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHACANCELACION)) = " + str(periodo -1)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:    
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " UNION ALL "   #Agregar las Demos 
    strSQL = strSQL + " SELECT nvl(COUNT (SAAD_FOLIO),0) as Cant, (0) as Total, ('') as tipoVenta from VT_VSALIDAAUTOSDEMO "
    strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND (Extract(Month from FECHAALTA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FECHAALTA)) = " + str(periodo -1)
    strSQL = strSQL + " AND SAAD_VEHI_CLASE <> 'US' "
    strSQL = strSQL + " UNION ALL "   #Agregar las Entregas del mes 
    strSQL = strSQL + " Select  COUNT(ET.ENTR_FOLIOENTREGA) AS Entregados, NVL(SUM(FAU_Venta),0) as Total, NVL(V.PEAU_TipoVenta,'') AS PEAU_TipoVenta "
    strSQL = strSQL + " From GM_ENTREGAUNIDAD  ET, VT_VLIBRODEVENTAS V "
    strSQL = strSQL + " Where ET.empr_empresaid =  " + str(bytEmpresa)
    strSQL = strSQL + " AND ET.ENTR_STATUS = 'AC' "
    strSQL = strSQL + " and ET.ENTR_VEHI_CLASE = 'NU' "
    strSQL = strSQL + " AND (Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo -1)
    strSQL = strSQL + " AND ET.empr_empresaid = v.Empr_empresaid "
    strSQL = strSQL + " AND ET.ENTR_FAAU_NOFACTURA = V.FAAU_NOFACTURA "
    strSQL = strSQL + " AND V.PEAU_TIPOVENTA <> 'INTERCAMB' "
    if bytSucursal != 3:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND V.PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND V.PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " GROUP BY V.PEAU_TipoVenta"

    c.execute(str(strSQL)) 
    numero_registro =0
    entregasant = 0
    for row in c:
        numero_registro +=1
        if numero_registro == 1:
            fecturasant =  int(row[0])
        elif numero_registro == 2:
            canceladasant = int(row[0]) 
        elif numero_registro == 3:
            intdemosant = int(row[0]) 
        elif numero_registro >= 4:
            entregasant = entregasant + int(row[0])

    
    conn.close()  

    intVentasAcum = intVentasAcum - intCanceladas

    facturasacumant = fecturasant - canceladasant
   
    return intVentasAcum, intEntregasGMF, intEntregasCont, facturasacumant, entregasant, intdemos, intdemosant

def obtiene_funel_asesores(bytAgencia, bytSucursal, mes, periodo):
    funel_dms = obtiene_fact_entregas_vendedor(bytAgencia, bytSucursal, mes, periodo)
    funel_sql, funel_objetivos, df_asesores = consultassql.obtiene_afluencia_vendedor(bytAgencia, bytSucursal, mes, periodo)

    funel_dms.columns=['numvendedor', 'concepto', 'cant']
    funel_sql.columns=['numvendedor', 'afluencia', 'solicitudes', 'aprobaciones', 'contratos']
    funel_objetivos.columns=['numvendedor','afluencia', 'solicitudes', 'demos', 'aprobaciones', 'facturacion', 'contratos', 'entregas']
    df_asesores.columns=['numvendedor', 'vendedor']

    # Pivoted funel_dms into funel_dms_pivot
    tmp_df = funel_dms[['numvendedor', 'concepto', 'cant']].copy()
    pivot_table = tmp_df.pivot_table(
    index=['numvendedor'],
    columns=['concepto'],
    values=['cant'],
    aggfunc={'cant': ['sum']}
    ).fillna(0)

    # # Rename the index axis
    pivot_table.columns=['canceladas', 'demos', 'entregas', 'facturas']
    funel_dms_pivot = pivot_table.reset_index()

    funel_dms_pivot['canceladas'] = funel_dms_pivot['canceladas'].fillna(0).astype('int')
    funel_dms_pivot['demos'] = funel_dms_pivot['demos'].fillna(0).astype('int')
    funel_dms_pivot['entregas'] = funel_dms_pivot['entregas'].fillna(0).astype('int')
    funel_dms_pivot['facturas'] = funel_dms_pivot['facturas'].fillna(0).astype('int')

    # Added column facturas
    funel_dms_pivot.insert(4, 'facturacion', 0)
    # Set formula of Facturas
    funel_dms_pivot['facturacion'] = funel_dms_pivot['facturas']-funel_dms_pivot['canceladas']

    # Eliminar las columnas que no necesitamos
    funel_dms_pivot.drop(['canceladas'], axis=1, inplace=True)
    funel_dms_pivot.drop(['facturas'], axis=1, inplace=True)

    # Renombrar columna de Demos
    funel_dms_pivot.rename(columns={'cant_sum_Demos': 'demos'}, inplace=True)

    # Unir los dos DataFrame
    df_merge = pd.merge(funel_sql, funel_dms_pivot, on='numvendedor')

    # Re ordenar las columnas
    df_merge_columns = [col for col in df_merge.columns if col != 'demos']
    df_merge_columns.insert(3, 'demos')
    df_merge = df_merge[df_merge_columns]

    df_merge_columns = [col for col in df_merge.columns if col != 'facturacion']
    df_merge_columns.insert(5, 'facturacion')
    df_merge = df_merge[df_merge_columns]

    # Aplicar la función melt para convertir las columnas en filas
    df_melted = df_merge.melt(id_vars=['numvendedor'], var_name='metrica', value_name='valor')

    # Aplicar la función melt para convertir las columnas en filas en los objetivos
    df_melted_obj = funel_objetivos.melt(id_vars=['numvendedor'], var_name='metrica', value_name='valor')

    # Unir los dos DataFrame por vendedor y concepto
    df_merge_general = pd.merge(df_melted, df_melted_obj, on=['numvendedor', 'metrica'])

    # # Rename the index axis
    df_merge_general.columns=['numvendedor', 'concepto', 'real', 'objetivo']

    # Added column porcentaje de avance
    df_merge_general.insert(4, 'avance', 0)
    # Set formula of Facturas
    df_merge_general['avance'] = df_merge_general.apply(lambda row: utilerias.calcular_porcentaje_avance(row['real'], row['objetivo']), axis=1)
    # df_merge_general['avance'] = (df_merge_general['real'] / df_merge_general['objetivo']) * 100

    # Unir el data frame con los vendedores para obtener los nombres
    df_final = pd.merge(df_asesores, df_merge_general, on='numvendedor')

    # Convertir el DataFrame a una lista de diccionarios
    tablavendedores = df_final.to_dict(orient='records')

    return tablavendedores 

def obtiene_fact_entregas_vendedor(bytAgencia, bytSucursal, mes, periodo):
    """
    Obtiene la informacion de vehiculos, ventas, entregas, cancelaciones para el funnel de asesores
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    datainicial = {
        'numvendedor': [0, 0, 0, 0],
        'concepto': ['Canceladas', 'Demos', 'Entregas', 'Facturas'],
        'cant': [0, 0 , 0, 0]
         }
    df_inicial = pd.DataFrame(datainicial)

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()
    
    # Ventas Acumuladas del ejercicio actual
    strSQL = "SELECT  PEAU_Vendedor as numvendedor, 'Facturas' as concepto, SUM(1) as cant " 
    strSQL = strSQL + " FROM VT_VLIBRODEVENTAS "
    strSQL = strSQL + " WHERE EMPR_EMPRESAID =  " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHA)) = " + str(periodo)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:    
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " Group by PEAU_Vendedor "
    strSQL = strSQL + " UNION ALL "   #Agregar las Canceladas 
    strSQL = strSQL + " SELECT  PEAU_Vendedor as numvendedor, 'Canceladas' as Concepto, SUM(1) as Cant  "
    strSQL = strSQL + " FROM VT_VLIBRODEVENTAS "
    strSQL = strSQL + " WHERE EMPR_EMPRESAID =  " + str(bytEmpresa)
    strSQL = strSQL + " AND (Extract(Month from FAAU_FECHACANCELACION)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FAAU_FECHACANCELACION)) = " + str(periodo)
    strSQL = strSQL + " AND VEHI_CLASE = 'NU'"
    strSQL = strSQL + " AND PEAU_TIPOVENTA <> 'INTERCAMB'"
    if bytSucursal != 3:    
        strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
        strSQL = strSQL + " AND PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND AGEN_IDAGENCIA = 1 "
        strSQL = strSQL + " AND PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " Group by PEAU_Vendedor "
    strSQL = strSQL + " UNION ALL "   #Agregar las Demos 
    strSQL = strSQL + " SELECT SAAD_VEND_CLAVE as numvendedor, 'Demos' as Concepto, nvl(COUNT (SAAD_FOLIO),0) as Cant "
    strSQL = strSQL + " From VT_VSALIDAAUTOSDEMO "
    strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL = strSQL + " AND AGEN_IDAGENCIA = " + str(bytSucursal)
    strSQL = strSQL + " AND (Extract(Month from FECHAALTA)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from FECHAALTA)) = " + str(periodo)
    strSQL = strSQL + " AND SAAD_VEHI_CLASE <> 'US' "
    strSQL = strSQL + " Group by SAAD_VEND_CLAVE "
    strSQL = strSQL + " UNION ALL "   #Agregar las Entregas del mes 
    strSQL = strSQL + " SELECT PEAU_Vendedor as numvendedor,  'Entregas' as Concepto, COUNT(ET.ENTR_FOLIOENTREGA) AS Entregados "
    strSQL = strSQL + " From GM_ENTREGAUNIDAD  ET, VT_VLIBRODEVENTAS V "
    strSQL = strSQL + " Where ET.empr_empresaid =  " + str(bytEmpresa)
    strSQL = strSQL + " AND ET.ENTR_STATUS = 'AC' "
    strSQL = strSQL + " and ET.ENTR_VEHI_CLASE = 'NU' "
    strSQL = strSQL + " AND (Extract(Month from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(mes)
    strSQL = strSQL + " AND (Extract(year from ET.ENTR_FECHAENTREGAUNIDAD)) = " + str(periodo)
    strSQL = strSQL + " AND ET.empr_empresaid = v.Empr_empresaid "
    strSQL = strSQL + " AND ET.ENTR_FAAU_NOFACTURA = V.FAAU_NOFACTURA "
    strSQL = strSQL + " AND V.PEAU_TIPOVENTA <> 'INTERCAMB' "
    if bytSucursal != 3:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = " + str(bytSucursal)
        strSQL = strSQL + " AND V.PEAU_TIPOVENTA not like '%FLOT%'"
    else:
        strSQL = strSQL + " AND ET.AGEN_IDAGENCIA  = 1 "
        strSQL = strSQL + " AND V.PEAU_TIPOVENTA like '%FLOT%'"
    strSQL = strSQL + " GROUP BY PEAU_Vendedor "
    strSQL = strSQL + " UNION ALL "
    strSQL = strSQL + " SELECT (0) as numvendedor, 'Facturas' as Concepto, (0) as Cant From DUAL "

    c.execute(str(strSQL)) 

    # Crear el DataFrame
    funel_tmp = pd.DataFrame.from_records(c)
    conn.close()  

    funel_tmp.columns=['numvendedor', 'concepto', 'cant']

    funel_dms = pd.concat([df_inicial, funel_tmp])
   
    return funel_dms

def resumen_inventario_x_paquete(bytAgencia, bytSucursal):
    """
    Obtiene el resumen de inventario en existencia, por modelo basico y paquete.
    y lo regresa en una tabla pivote
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    # Obtener el resultado 
    strSQL = "Select (Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ) as modelobasico, "
    strSQL = strSQL + " v.mode_tipo, count(v.vehi_numeroinventario) as cantidad "
    strSQL = strSQL + " FROM vt_vinventarioautos v, vt_modelos m "
    strSQL = strSQL + " WHERE V.Empr_Empresaid = " + str(bytEmpresa)
    strSQL = strSQL + " and V.VEHI_STATUS = 'AC' "
    strSQL = strSQL + " and V.VEHI_CLAS_CLAVE  <> 'US' "
    strSQL = strSQL + " and m.empr_empresaid = v.empr_empresaid "
    strSQL = strSQL + " and M.MODE_CLAVE = V.MODE_CLAVE "
    strSQL = strSQL + " and m.mode_tipo = v.mode_tipo "
    strSQL = strSQL + " group by (Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ), v.mode_tipo "
    strSQL = strSQL + " order by (Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ), v.mode_tipo "

    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consultaentrega = pd.DataFrame.from_records(c)
    df_consultaentrega.columns = ['modelo', 'paq', 'cant']

    # Crear la tabla pivot en un nuevo DataFrame
    df=df_consultaentrega.pivot(index='modelo', columns='paq', values='cant').fillna(0)

    df_final = agregar_totales(df, "Total General")

    df_final.columns = [flatten_column_header(col) for col in df.columns]

    conn.close

    return df_final

def resumen_inventario_x_paquete_consolidado():
    """
    Obtiene el resumen de inventario en existencia, por modelo basico y paquete.
    y lo regresa en una tabla pivote
    """

    df_acumulado = pd.DataFrame()

    empresas = ['1', '3', '5']
    for empresa in empresas:
        
        bytEmpresa = 1
        if empresa == cadillac:
            bytEmpresa = 2

        conn = None
        conn = config.creaconeccion(empresa)
        c = conn.cursor()

        # Obtener el resultado 
        strSQL = "Select (Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ) as modelobasico, "
        strSQL = strSQL + " v.mode_tipo, count(v.vehi_numeroinventario) as cantidad "
        strSQL = strSQL + " FROM vt_vinventarioautos v, vt_modelos m "
        strSQL = strSQL + " WHERE V.Empr_Empresaid = " + str(bytEmpresa)
        strSQL = strSQL + " and V.VEHI_STATUS = 'AC' "
        strSQL = strSQL + " and V.VEHI_CLAS_CLAVE  <> 'US' "
        strSQL = strSQL + " and m.empr_empresaid = v.empr_empresaid "
        strSQL = strSQL + " and M.MODE_CLAVE = V.MODE_CLAVE "
        strSQL = strSQL + " and m.mode_tipo = v.mode_tipo "
        strSQL = strSQL + " group by (Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ), v.mode_tipo "
        strSQL = strSQL + " order by (Case When INSTR(mode_basico, ' ') > 0 Then SUBSTR(mode_basico, 1, INSTR(mode_basico, ' ') - 1) else mode_basico end ), v.mode_tipo "

        c.execute(str(strSQL)) 

        # Crear el DataFrame
        df_consulta = pd.DataFrame.from_records(c)
        df_consulta.columns = ['modelo', 'paq', 'cant']
        # Concatenar el DataFrame de la empresa actual al DataFrame consolidado
        df_acumulado = pd.concat([df_acumulado, df_consulta], axis=0)

    # Crear la tabla pivot en un nuevo DataFrame
    # Realizar una agregación para evitar índices duplicados
    df_acumulado = df_acumulado.groupby(['modelo', 'paq']).agg({'cant': 'sum'}).reset_index()
    df=df_acumulado.pivot(index='modelo', columns='paq', values='cant').fillna(0)

    df_final = agregar_totales(df, "Total General")

    df_final.columns = [flatten_column_header(col) for col in df.columns]

    conn.close

    return df_final

def inventario_detalle(bytAgencia, bytSucursal):
    """
    Obtiene el detalle de inventario en existencia, por modelo basico y paquete.
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    # Obtener el resultado 
    strSQL = " SELECT (V.VEHI_CLASE || '-' || V.VEHI_ANIO || '-' || V.VEHI_NUMEROINVENTARIO) as INVENTARIO, V.MODE_DESCRIPCION, V.Mode_tipo,  V.VEHI_SERIE, "
    strSQL += " TO_DATE(V.VEHI_FECHAASIGNACION, 'DD/MM/YY') AS FECHAASIGN, TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY') AS FECHAINTERES, "
    strSQL += " (Trunc(Sysdate) - Trunc(TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY'))) as diasPP,  (Ve.Colo_descrip || ' | ' ||  VI.Colo_Descrip) as Color, "
    strSQL += " V.VEHI_ANIO_MODELO, v.UBIC_DESCRIPCION, NVL(V.vehi_ignitionkey, ' ') as Apartado , "
    strSQL += " nvl (( SELECT PP.PRIM_SALDO * -1 FROM VT_PRIMPLANPISO PP "
    strSQL += "         WHERE PP.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += "         AND PP.PRIM_VEHI_CLASE = V.VEHI_CLAS_CLAVE "
    strSQL += "         AND PP.PRIM_VEHI_ANIO = V.VEHI_ANIO "
    strSQL += "         AND PP.PRIM_VEHI_NUMEROINVENTARIO = V.VEHI_NUMEROINVENTARIO "
    strSQL += "     ), 0) AS PRIM_SALDO, V.VEHI_COSTOFACTURA, V.VEHI_CLASE "
    strSQL += " FROM  vt_vinventarioautos V, VT_Colores VE, vt_Colores VI "
    strSQL += " WHERE V.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL += " AND V.VEHI_STATUS = 'AC' "
    if bytSucursal == 3:
        strSQL += " AND V.UBIC_DESCRIPCION like ('%FLOT%') "
    else:
        strSQL += " AND V.UBIC_DESCRIPCION not like ('%FLOT%') "
    strSQL += " AND VE.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += " AND VE.Colo_clave = V.Vehi_colo_Claveext1 "
    strSQL += " AND VE.Colo_Mode_clave = V.MODE_CLAVE "
    strSQL += " AND VI.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += " AND VI.Colo_clave = V.Vehi_colo_Claveext1 "
    strSQL += " AND VI.Colo_Mode_clave = V.MODE_CLAVE "
    strSQL += " ORDER BY diasPP DESC,  V.VEHI_CLASE, V.VEHI_ANIO, V.VEHI_NUMEROINVENTARIO "

    c.execute(strSQL) 

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns =['inv', 'descm', 'paq', 'vin', 'fasignacion', 'finteres', 'diaspp', 'color', 'modelo', 'ubicacion', 'observaciones', 'saldopp', 'costo', 'clase']
    # Convierte las columnas al tipo datetime
    df_consulta['fasignacion'] = pd.to_datetime(df_consulta['fasignacion'])
    df_consulta['finteres'] = pd.to_datetime(df_consulta['finteres'])
    # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
    df_consulta[['fasignacion', 'finteres']] = df_consulta[['fasignacion', 'finteres']].applymap(lambda x: x.strftime('%d/%m/%y'))
    # Limitar el numero de caracteres por columna
    df_consulta['descm'] = df_consulta['descm'].str[:30]
    df_consulta['vin'] = df_consulta['vin'].str[-8:]

     # Separar los nuevos y los seminuevos
    filtrousados = df_consulta["clase"].str.contains("US", case=False)
    df_nuevos = df_consulta[~filtrousados].copy()
    df_seminuevos = df_consulta[filtrousados].copy()

    conn.close

    return df_nuevos, df_seminuevos

def resumeninvxagencia(bytAgencia, bytSucursal):
    """
    Obtiene el resumen de inventario en existencia, por tipo de vehiculo, dias de antiguedad y antiguedad promedio
    y lo regresa en una tabla pivote
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strempresa = config.obtiene_empresa(bytAgencia, bytSucursal)

    # Obtener el resultado de la tabla del DMS
    strSQL = " SELECT (V.VEHI_CLASE || '-' || V.VEHI_ANIO || '-' || V.VEHI_NUMEROINVENTARIO) as INVENTARIO, V.MODE_DESCRIPCION, V.Mode_tipo,  V.VEHI_SERIE, "
    strSQL += " TO_DATE(V.VEHI_FECHAASIGNACION, 'DD/MM/YY') AS FECHAASIGN, TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY') AS FECHAINTERES, "
    strSQL += " (Trunc(Sysdate) - Trunc(TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY'))) as diasPP,  (Ve.Colo_descrip || ' | ' ||  VI.Colo_Descrip) as Color, "
    strSQL += " V.VEHI_ANIO_MODELO, v.UBIC_DESCRIPCION, NVL(V.vehi_ignitionkey, ' ') as Apartado , "
    strSQL += " nvl (( SELECT PP.PRIM_SALDO * -1 FROM VT_PRIMPLANPISO PP "
    strSQL += "         WHERE PP.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += "         AND PP.PRIM_VEHI_CLASE = V.VEHI_CLAS_CLAVE "
    strSQL += "         AND PP.PRIM_VEHI_ANIO = V.VEHI_ANIO "
    strSQL += "         AND PP.PRIM_VEHI_NUMEROINVENTARIO = V.VEHI_NUMEROINVENTARIO "
    strSQL += "     ), 0) AS PRIM_SALDO, V.VEHI_COSTOFACTURA, VEHI_CLAS_CLAVE, TO_DATE(VEHI_FECHAASIGNACION, 'DD/MM/YY') AS FECHA,  TO_DATE(VEHI_FECHAVENCIMIENTO, 'DD/MM/YY') AS FECHAVENCIMIENTO "
    strSQL += " FROM  vt_vinventarioautos V, VT_Colores VE, vt_Colores VI "
    strSQL += " WHERE V.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL += " AND V.VEHI_STATUS = 'AC' "
    if bytSucursal == 3:
        strSQL += " AND V.UBIC_DESCRIPCION like ('%FLOT%') "
    else:
        strSQL += " AND V.UBIC_DESCRIPCION not like ('%FLOT%') "
    strSQL += " AND VE.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += " AND VE.Colo_clave = V.Vehi_colo_Claveext1 "
    strSQL += " AND VE.Colo_Mode_clave = V.MODE_CLAVE "
    strSQL += " AND VI.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += " AND VI.Colo_clave = V.Vehi_colo_Claveext1 "
    strSQL += " AND VI.Colo_Mode_clave = V.MODE_CLAVE "
    strSQL += " ORDER BY diasPP DESC,  V.VEHI_CLASE, V.VEHI_ANIO, V.VEHI_NUMEROINVENTARIO "

    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns =['inv', 'descm', 'paq', 'vin', 'fasignacion', 'finteres', 'diaspp', 'color', 'modelo', 'ubicacion', 'observaciones', 'saldopp', 'costo', 'Clase', 'Fecha', 'FechaVencimiento']
    # Convierte las columnas al tipo datetime
    df_consulta['fasignacion'] = pd.to_datetime(df_consulta['fasignacion'])
    df_consulta['finteres'] = pd.to_datetime(df_consulta['finteres'])
    # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
    df_consulta[['fasignacion', 'finteres']] = df_consulta[['fasignacion', 'finteres']].applymap(lambda x: x.strftime('%d/%m/%y'))
    # Limitar el numero de caracteres por columna
    df_consulta['descm'] = df_consulta['descm'].str[:30]
    df_consulta['vin'] = df_consulta['vin'].str[-8:]

    
    # Convertir la columna 'Fecha' al tipo datetime
    df_consulta['Fecha'] = pd.to_datetime(df_consulta['Fecha'], format='%d/%m/%Y')
    df_consulta['FechaVencimiento'] = pd.to_datetime(df_consulta['FechaVencimiento'], format='%d/%m/%Y')

    # Estadísticas
    total_registros = len(df_consulta)
    total_nu = len(df_consulta[df_consulta['Clase'] == 'NU'])
    total_de = len(df_consulta[df_consulta['Clase'] == 'DE'])
    total_us = len(df_consulta[df_consulta['Clase'] == 'US'])
    dias_mas_antiguo = (datetime.now() - df_consulta['Fecha'].min()).days
    antiguedad_promedio = (datetime.now() - df_consulta['Fecha']).mean().days

    # Fecha actual
    fecha_actual = datetime.now()

    # Calcula los días vencidos para cada fecha
    df_consulta['DiasVencidos'] = (fecha_actual - df_consulta['FechaVencimiento']).dt.days

    # Filtrar los registros vencidos
    vencidos_total = df_consulta[df_consulta['DiasVencidos'] > 0].shape[0]
    vencidos_30_90 = df_consulta[(df_consulta['DiasVencidos'] >= 30) & (df_consulta['DiasVencidos'] < 90)]
    vencidos_90_180 = df_consulta[(df_consulta['DiasVencidos'] >= 90) & (df_consulta['DiasVencidos'] < 180)]
    vencidos_mas_180 = df_consulta[df_consulta['DiasVencidos'] >= 180]

    strlogo = strempresa.logo
    strbg = strempresa.bg_color
    if bytEmpresa == 2:
        strlogo = "admin-lte/dist/img/logo_cadillac.jpg"
        strbg = "bg-warning"

    datos = {
        'nombre_empresa': strempresa.nombre_empresa,
        'empresa': str(bytAgencia), 
        'sucursal': str(bytSucursal),
        'totalinv': total_registros,
        'nu': total_nu,
        'de': total_de,
        'us': total_us,
        'diasmas': dias_mas_antiguo,
        'prom': antiguedad_promedio,
        'vencidos': vencidos_total,
        '30': vencidos_30_90.shape[0],
        '30porc': utilerias.calcula_porcentaje_valor(vencidos_30_90.shape[0], vencidos_total),
        '90': vencidos_90_180.shape[0],
        '90porc': utilerias.calcula_porcentaje_valor(vencidos_90_180.shape[0], vencidos_total),
        '180': vencidos_mas_180.shape[0],
        '180porc':utilerias.calcula_porcentaje_valor(vencidos_mas_180.shape[0], vencidos_total),
        'detalle30': vencidos_30_90.to_dict(orient='records'), 
        'detalle90': vencidos_90_180.to_dict(orient='records'), 
        'detalle180': vencidos_mas_180.to_dict(orient='records'),
        'logo': strlogo,
        'bg': strbg
        }

    return datos

def resumen_planpiso(bytAgencia, bytSucursal):
    """
    Obtiene el resumen de inventario en existencia, por tipo de vehiculo, dias de antiguedad y antiguedad promedio
    y lo regresa en una tabla pivote
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strempresa = config.obtiene_empresa(bytAgencia, bytSucursal)

    # Obtener el resultado de la tabla del DMS
    strSQL = " SELECT (V.VEHI_CLASE || '-' || V.VEHI_ANIO || '-' || V.VEHI_NUMEROINVENTARIO) as INVENTARIO, V.MODE_DESCRIPCION, V.Mode_tipo,  V.VEHI_SERIE, "
    strSQL += " TO_DATE(V.VEHI_FECHAASIGNACION, 'DD/MM/YY') AS FECHAASIGN, TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY') AS FECHAINTERES, "
    strSQL += " (Trunc(Sysdate) - Trunc(TO_DATE(V.VEHI_FECHAVENCIMIENTO, 'DD/MM/YY'))) as diasPP,  (Ve.Colo_descrip || ' | ' ||  VI.Colo_Descrip) as Color, "
    strSQL += " V.VEHI_ANIO_MODELO, v.UBIC_DESCRIPCION, NVL(V.vehi_ignitionkey, ' ') as Apartado , "
    strSQL += " nvl (( SELECT PP.PRIM_SALDO * -1 FROM VT_PRIMPLANPISO PP "
    strSQL += "         WHERE PP.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += "         AND PP.PRIM_VEHI_CLASE = V.VEHI_CLAS_CLAVE "
    strSQL += "         AND PP.PRIM_VEHI_ANIO = V.VEHI_ANIO "
    strSQL += "         AND PP.PRIM_VEHI_NUMEROINVENTARIO = V.VEHI_NUMEROINVENTARIO "
    strSQL += "     ), 0) AS PRIM_SALDO, V.VEHI_COSTOFACTURA, VEHI_CLAS_CLAVE, TO_DATE(VEHI_FECHAASIGNACION, 'DD/MM/YY') AS FECHA,  TO_DATE(VEHI_FECHAVENCIMIENTO, 'DD/MM/YY') AS FECHAVENCIMIENTO "
    strSQL += " FROM  vt_vinventarioautos V, VT_Colores VE, vt_Colores VI "
    strSQL += " WHERE V.EMPR_EMPRESAID = " + str(bytEmpresa)
    strSQL += " AND V.VEHI_STATUS = 'AC' "
    if bytSucursal == 3:
        strSQL += " AND V.UBIC_DESCRIPCION like ('%FLOT%') "
    else:
        strSQL += " AND V.UBIC_DESCRIPCION not like ('%FLOT%') "
    strSQL += " AND VE.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += " AND VE.Colo_clave = V.Vehi_colo_Claveext1 "
    strSQL += " AND VE.Colo_Mode_clave = V.MODE_CLAVE "
    strSQL += " AND VI.EMPR_EMPRESAID = V.EMPR_EMPRESAID "
    strSQL += " AND VI.Colo_clave = V.Vehi_colo_Claveext1 "
    strSQL += " AND VI.Colo_Mode_clave = V.MODE_CLAVE "
    strSQL += " ORDER BY diasPP DESC,  V.VEHI_CLASE, V.VEHI_ANIO, V.VEHI_NUMEROINVENTARIO "

    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns =['inv', 'descm', 'paq', 'vin', 'fasignacion', 'finteres', 'diaspp', 'color', 'modelo', 'ubicacion', 'observaciones', 'saldopp', 'costo', 'Clase', 'Fecha', 'FechaVencimiento']
    # Convierte las columnas al tipo datetime
    df_consulta['fasignacion'] = pd.to_datetime(df_consulta['fasignacion'])
    df_consulta['finteres'] = pd.to_datetime(df_consulta['finteres'])
    # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
    df_consulta[['fasignacion', 'finteres']] = df_consulta[['fasignacion', 'finteres']].applymap(lambda x: x.strftime('%d/%m/%y'))
    # Limitar el numero de caracteres por columna
    df_consulta['descm'] = df_consulta['descm'].str[:30]
    df_consulta['vin'] = df_consulta['vin'].str[-8:]

    
    # Convertir la columna 'Fecha' al tipo datetime
    df_consulta['Fecha'] = pd.to_datetime(df_consulta['Fecha'], format='%d/%m/%Y')
    df_consulta['FechaVencimiento'] = pd.to_datetime(df_consulta['FechaVencimiento'], format='%d/%m/%Y')

    # Estadísticas
    total_registros = len(df_consulta)
    total_nu = len(df_consulta[df_consulta['Clase'] == 'NU'])
    total_de = len(df_consulta[df_consulta['Clase'] == 'DE'])
    total_us = len(df_consulta[df_consulta['Clase'] == 'US'])
    dias_mas_antiguo = (datetime.now() - df_consulta['Fecha'].min()).days
    antiguedad_promedio = (datetime.now() - df_consulta['Fecha']).mean().days

    # Fecha actual
    fecha_actual = datetime.now()

    # Calcula los días vencidos para cada fecha
    df_consulta['DiasVencidos'] = (fecha_actual - df_consulta['FechaVencimiento']).dt.days

    # Filtrar los registros vencidos
    vencidos_total = df_consulta[df_consulta['DiasVencidos'] > 0].shape[0]
    vencidos_30_90 = df_consulta[(df_consulta['DiasVencidos'] >= 30) & (df_consulta['DiasVencidos'] < 90)]
    vencidos_90_180 = df_consulta[(df_consulta['DiasVencidos'] >= 90) & (df_consulta['DiasVencidos'] < 180)]
    vencidos_mas_180 = df_consulta[df_consulta['DiasVencidos'] >= 180]

    strlogo = strempresa.logo
    strbg = strempresa.bg_color
    if bytEmpresa == 2:
        strlogo = "admin-lte/dist/img/logo_cadillac.jpg"
        strbg = "bg-warning"

    datos = {
        'nombre_empresa': strempresa.nombre_empresa,
        'empresa': str(bytAgencia), 
        'sucursal': str(bytSucursal),
        'totalinv': total_registros,
        'nu': total_nu,
        'de': total_de,
        'us': total_us,
        'diasmas': dias_mas_antiguo,
        'prom': antiguedad_promedio,
        'vencidos': vencidos_total,
        '30': vencidos_30_90.shape[0],
        '30porc': utilerias.calcula_porcentaje_valor(vencidos_30_90.shape[0], vencidos_total),
        '90': vencidos_90_180.shape[0],
        '90porc': utilerias.calcula_porcentaje_valor(vencidos_90_180.shape[0], vencidos_total),
        '180': vencidos_mas_180.shape[0],
        '180porc':utilerias.calcula_porcentaje_valor(vencidos_mas_180.shape[0], vencidos_total),
        'detalle30': vencidos_30_90.to_dict(orient='records'), 
        'detalle90': vencidos_90_180.to_dict(orient='records'), 
        'detalle180': vencidos_mas_180.to_dict(orient='records'),
        'logo': strlogo,
        'bg': strbg
        }

    return datos

def resumen_cuentasxcobrar(bytAgencia, bytSucursal):
    """
    Obtiene el resumen de las cuentas x cobrar por antiguedad 
    y lo regresa en una tabla pivote
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strempresa = config.obtiene_empresa(bytAgencia, bytSucursal)

    # Obtener el resultado de la tabla del DMS
    strSQL = " Select c.Clie_clave, (Case when nvl(c.clie_razonsocial, ' ') <> ' ' then c.clie_razonsocial else c.Clie_nombre || ' ' || c.clie_apellidopaterno end) as Nombre, "
    strSQL += " TO_DATE(CP.PRIM_FECHAVENCIMIENTO) as VENCIMIENTO, cp.prim_saldo, CP.PRIM_OBSERVACIONES, TC.TIPO_DESCRIPCION, TC.TIPO_CARTERASDO "
    strSQL += " From CLIENTES C ,  CC_PRIMCLIENTES CP, CC_TIPOSCARTERA TC "
    strSQL += " where C.empr_empresaid  = " + str(bytEmpresa)
    strSQL += " and cp.empr_empresaid = c.empr_empresaid "
    strSQL += " and CP.PRIM_CLIE_CLAVE = c.Clie_clave "
    strSQL += " and cp.prim_saldo <> 0 "
    if strempresa.ref_cartera != "*":
        strSQL += " AND CP.PRIM_REFERENCIA3 LIKE ('%" + str(strempresa.ref_cartera) + "%')"
    if bytSucursal == 3:
        strSQL += " AND CP.PRIM_TIPOVENTA LIKE ('%FLOT%')"
    else:
        strSQL += " AND CP.PRIM_TIPOVENTA NOT LIKE ('%FLOT%')"
    strSQL += " AND TC.EMPR_EMPRESAID = Cp.EMPR_EMPRESAID "
    strSQL += " AND TC.TIPO_CARTERA = CP.PRIM_CARTERA "
    strSQL += " Order by c.Clie_clave "

    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns =['cliente', 'nombre', 'fvencimiento', 'saldo', 'comentarios', 'tipocartera', 'grupocartera']
    # Convierte las columnas al tipo datetime
    df_consulta['fvencimiento'] = pd.to_datetime(df_consulta['fvencimiento'])
    # Cambia el formato de las columnas 'fecfactura' y 'feccancelacion' en el mismo DataFrame
    # df_consulta[['fvencimiento']] = df_consulta[['fvencimiento']].applymap(lambda x: x.strftime('%d/%m/%y'))

    # Fecha actual
    fecha_actual = datetime.now()
    # Calcula los días vencidos para cada fecha
    df_consulta['DiasVencidos'] = (fecha_actual - df_consulta['fvencimiento']).dt.days
    # Filtrar los registros vencidos
    vencidos_total = df_consulta[df_consulta['DiasVencidos'] > 0]

    df_auto = vencidos_total[vencidos_total['grupocartera'] == 'AUTO']
    df_refa = vencidos_total[vencidos_total['grupocartera'] == 'REFA']
    df_serv = vencidos_total[vencidos_total['grupocartera'] == 'SERV']

    dias_mas_antiguo = (datetime.now() - vencidos_total['fvencimiento'].min()).days
    antiguedad_promedio = (datetime.now() - vencidos_total['fvencimiento']).mean().days

    vencidos_0 = df_consulta[df_consulta['DiasVencidos'] <= 0]
    vencidos_1_30 = df_consulta[(df_consulta['DiasVencidos'] >= 1) & (df_consulta['DiasVencidos'] < 30)]
    vencidos_30_60 = df_consulta[(df_consulta['DiasVencidos'] >= 30) & (df_consulta['DiasVencidos'] < 60)]
    vencidos_60_90 = df_consulta[(df_consulta['DiasVencidos'] >= 60) & (df_consulta['DiasVencidos'] < 90)]
    vencidos_mas_90 = df_consulta[df_consulta['DiasVencidos'] >= 90]

    saldo_vencido = vencidos_total['saldo'].sum()
    saldo_total = df_consulta['saldo'].sum()

    strlogo = strempresa.logo
    strbg = strempresa.bg_color

    datos = {
        'nombre_empresa': strempresa.nombre_empresa,
        'empresa': str(bytAgencia), 
        'sucursal': str(bytSucursal),
        'totalcartera': df_consulta['saldo'].sum(),
        'totalvencido': vencidos_total['saldo'].sum(),
        'auto': df_auto['saldo'].sum(),
        'refa': df_refa['saldo'].sum(),
        'serv': df_serv['saldo'].sum(),
        'diasmas': dias_mas_antiguo,
        'prom': antiguedad_promedio,
        'vigente': vencidos_0['saldo'].sum(),
        'vigentep': utilerias.calcula_porcentaje_valor(vencidos_0['saldo'].sum(), saldo_total),
        '1a30': vencidos_1_30['saldo'].sum(),
        '1a30p': utilerias.calcula_porcentaje_valor(vencidos_1_30['saldo'].sum(), saldo_total),
        '30a60': vencidos_30_60['saldo'].sum(),
        '30a60p': utilerias.calcula_porcentaje_valor(vencidos_30_60['saldo'].sum(), saldo_total),
        '60a90': vencidos_60_90['saldo'].sum(),
        '60a90p': utilerias.calcula_porcentaje_valor(vencidos_60_90['saldo'].sum(), saldo_total),
        '90': vencidos_mas_90['saldo'].sum(),
        '90p': utilerias.calcula_porcentaje_valor(vencidos_mas_90['saldo'].sum(), saldo_total),
        'logo': strlogo,
        'bg': strbg
        }

    return datos

def concat_unique_comments(comments):
    unique_comments = set(filter(None, comments))  # Filtrar comentarios no nulos y eliminar duplicados
    return ' - '.join(unique_comments)  # Concatenar comentarios únicos
        
def detalle_cuentasxcobrar(bytAgencia, bytSucursal):
    """
    Obtiene el resumen de las cuentas x cobrar por antiguedad 
    y lo regresa en una tabla pivote
    """
    bytEmpresa = 1
    if bytAgencia == cadillac:
        bytEmpresa = 2

    conn = None
    conn = config.creaconeccion(bytAgencia)
    c = conn.cursor()

    strempresa = config.obtiene_empresa(bytAgencia, bytSucursal)

    # Obtener el resultado de la tabla del DMS
    strSQL = " Select c.Clie_clave, (Case when nvl(c.clie_razonsocial, ' ') <> ' ' then c.clie_razonsocial else c.Clie_nombre || ' ' || c.clie_apellidopaterno end) as Nombre, "
    strSQL += " CP.PRIM_IMPORTE, cp.prim_saldo, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) < 0 Then cp.prim_saldo else 0 end ) as vigente, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 0 AND (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) <= 30 Then cp.prim_saldo else 0 end ) as dias30, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 30 AND (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) <= 60 Then cp.prim_saldo else 0 end ) as dias60, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 60 AND (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) <= 90 Then cp.prim_saldo else 0 end ) as dias90, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 90 Then cp.prim_saldo else 0 end ) as mas90, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 0 Then cp.prim_saldo else 0 end ) as totalvencido, "
    strSQL += " CP.PRIM_OBSERVACIONES, TC.TIPO_CARTERASDO "
    strSQL += " From CLIENTES C ,  CC_PRIMCLIENTES CP, CC_TIPOSCARTERA TC "
    strSQL += " where C.empr_empresaid  = " + str(bytEmpresa)
    strSQL += " and cp.empr_empresaid = c.empr_empresaid "
    strSQL += " and CP.PRIM_CLIE_CLAVE = c.Clie_clave "
    strSQL += " and cp.prim_saldo <> 0 "
    if strempresa.ref_cartera != "*":
        strSQL += " AND CP.PRIM_REFERENCIA3 LIKE ('%" + str(strempresa.ref_cartera) + "%')"
    if bytSucursal == 3:
        strSQL += " AND CP.PRIM_TIPOVENTA LIKE ('%FLOT%')"
    else:
        strSQL += " AND CP.PRIM_TIPOVENTA NOT LIKE ('%FLOT%')"
    strSQL += " AND TC.EMPR_EMPRESAID = Cp.EMPR_EMPRESAID "
    strSQL += " AND TC.TIPO_CARTERA = CP.PRIM_CARTERA "
    strSQL += " Order by c.Clie_clave "

    print(str(bytSucursal))

    c.execute(str(strSQL)) 

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns = ['cliente', 'nombre', 'importe', 'totalcxc', 'vigente', '30','60', '90', 'mas_90', 'totalvencido', 'comentarios', 'grupocartera']

    # Agrupar el DataFrame df_totals por cliente y grupocartera, concatenando los comentarios
    df_grouped_totals = df_consulta.groupby(['cliente', 'grupocartera']).agg({
        'nombre': 'first',  # Tomar el primer valor del nombre
        'importe': 'sum',
        'totalcxc': 'sum',
        'vigente': 'sum',
        '30': 'sum',
        '60': 'sum',
        '90': 'sum',
        'mas_90': 'sum',
        'totalvencido': 'sum',
        'comentarios': concat_unique_comments  # Utilizar la función de concatenación de comentarios únicos
    }).reset_index()

   # Calcular los totales para la fila "TOTAL"
    total_row = df_grouped_totals.drop(['cliente', 'grupocartera', 'comentarios'], axis=1).sum().fillna(0)
    total_row['nombre'] = 'TOTAL CARTERA'  # Agregar el nombre "TOTAL"

    # Crear un DataFrame con la fila "TOTAL"
    df_total_row = pd.DataFrame([total_row], columns=df_grouped_totals.columns)

    # Concatenar df_grouped_totals y df_total_row
    df_final = pd.concat([df_grouped_totals, df_total_row], ignore_index=True).fillna(' ')

    # Concatenar df_final con df_total usando concat
    # df_final = pd.concat([df_final, df_total], axis=1)

    return df_final

def completar_columnas(df, nombretotal="TOTAL", cuantas = 12):
    """
    funcion para llenar las 12 columnas de meses, para la tabla pivot de las ventas y entregas
    """
    # Verificar la cantidad de columnas actuales
    num_columnas_actuales = df.shape[1]


    # Calcular la cantidad de columnas que faltan agregar
    num_columnas_faltantes = cuantas - num_columnas_actuales

    # Generar las columnas adicionales con valores en cero
    columnas_adicionales = [f'Columna{i}' for i in range(num_columnas_actuales + 1, num_columnas_actuales + num_columnas_faltantes + 1)]
    datos_columnas_adicionales = pd.DataFrame({col: 0 for col in columnas_adicionales}, index=df.index)


    # Combinar el DataFrame original con las columnas adicionales
    df_completo = pd.concat([df, datos_columnas_adicionales], axis=1)
    # Calcular el total por columna
    # df_completo.loc[nombretotal] = df_completo.sum()

    # # Calcular el total por registro
    # df_completo['Total Registro'] = df_completo.sum(axis=1)

    # df_ordenado = df_completo.sort_values('Total Registro', ascending=False)

    return df_completo

def agregar_totales(df, nombretotal="TOTAL"):
    """
    funcion para agregar los totales a un dataframa
    """
  
    # Calcular el total por columna
    df.loc[nombretotal] = df.sum()

    # # Calcular el total por registro
    df['Total Registro'] = df.sum(axis=1)

    # df_ordenado = df_completo.sort_values('Total Registro', ascending=False)

    return df

# Función para aplanar los nombres de las columnas§
def flatten_column_header(col):
    return ''.join(str(c) for c in col)
from dashboards.utilerias import config
from datetime import datetime, date, timedelta
import pandas as pd
from  .utils import calcula_porcentaje_valor

cadillac = 7    # Constante para la empresa cadillac

def concat_unique_comments(comments):
    unique_comments = set(filter(None, comments))  # Filtrar comentarios no nulos y eliminar duplicados
    return ' - '.join(unique_comments)  # Concatenar comentarios únicos


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
    conn.close

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
        'vigentep': calcula_porcentaje_valor(vencidos_0['saldo'].sum(), saldo_total),
        '1a30': vencidos_1_30['saldo'].sum(),
        '1a30p': calcula_porcentaje_valor(vencidos_1_30['saldo'].sum(), saldo_total),
        '30a60': vencidos_30_60['saldo'].sum(),
        '30a60p': calcula_porcentaje_valor(vencidos_30_60['saldo'].sum(), saldo_total),
        '60a90': vencidos_60_90['saldo'].sum(),
        '60a90p': calcula_porcentaje_valor(vencidos_60_90['saldo'].sum(), saldo_total),
        '90': vencidos_mas_90['saldo'].sum(),
        '90p': calcula_porcentaje_valor(vencidos_mas_90['saldo'].sum(), saldo_total),
        'logo': strlogo,
        'bg': strbg
        }

    return datos

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

    c.execute(str(strSQL)) 
    conn.close

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

    # Ordenar primero por la columna 'Edad' de forma descendente y luego por 'Puntuación' de forma ascendente
    df_final = df_final.sort_values(by=['totalvencido', 'totalcxc'], ascending=[False, False])

    return df_final

def resumen_cuentasxpagar(bytAgencia, bytSucursal):
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
    strSQL = " SELECT c.PROV_clave, (c.prov_razonsocial) as Nombre,  TO_DATE(CP.PRIM_FECHAVENCIMIENTO) as VENCIMIENTO, (CP.PRIM_SALDO * -1) as SALDO, CP.PRIM_ORIGEN "
    strSQL += " From PROVEEDORES C ,  CP_PRIMPROVEEDORES CP  "
    strSQL += " where C.empr_empresaid  = " + str(bytEmpresa)
    strSQL += " and cp.empr_empresaid = c.empr_empresaid "
    strSQL += " and CP.PRIM_PROV_CLAVE = c.PROV_CLAVE "
    strSQL += " and cp.prim_saldo <> 0 "
    if strempresa.ref_cartera != "*":
        strSQL += " AND CP.PRIM_REFERENCIA3 LIKE ('%" + str(strempresa.ref_cartera) + "%')"
    strSQL += " Order by c.PROV_CLAVE "

    c.execute(str(strSQL)) 
    conn.close

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns =['cliente', 'nombre', 'fvencimiento', 'saldo', 'origen']
    # Convierte las columnas al tipo datetime
    df_consulta['fvencimiento'] = pd.to_datetime(df_consulta['fvencimiento'])

    # Fecha actual
    fecha_actual = datetime.now()
    # Calcula los días vencidos para cada fecha
    df_consulta['DiasVencidos'] = (fecha_actual - df_consulta['fvencimiento']).dt.days
    # Filtrar los registros vencidos
    vencidos_total = df_consulta[df_consulta['DiasVencidos'] > 0]


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
        'diasmas': dias_mas_antiguo,
        'prom': antiguedad_promedio,
        'vigente': vencidos_0['saldo'].sum(),
        'vigentep': calcula_porcentaje_valor(vencidos_0['saldo'].sum(), saldo_total),
        '1a30': vencidos_1_30['saldo'].sum(),
        '1a30p': calcula_porcentaje_valor(vencidos_1_30['saldo'].sum(), saldo_total),
        '30a60': vencidos_30_60['saldo'].sum(),
        '30a60p': calcula_porcentaje_valor(vencidos_30_60['saldo'].sum(), saldo_total),
        '60a90': vencidos_60_90['saldo'].sum(),
        '60a90p': calcula_porcentaje_valor(vencidos_60_90['saldo'].sum(), saldo_total),
        '90': vencidos_mas_90['saldo'].sum(),
        '90p': calcula_porcentaje_valor(vencidos_mas_90['saldo'].sum(), saldo_total),
        'logo': strlogo,
        'bg': strbg
        }

    return datos

def detalle_cuentasxpagar(bytAgencia, bytSucursal):
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
    strSQL = " Select c.PROV_clave, (c.prov_razonsocial) as Nombre, (CP.PRIM_IMPORTE * -1 ) as importe, (CP.PRIM_SALDO * -1) as SALDO,   "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) < 0 Then (CP.PRIM_SALDO * -1) else 0 end ) as vigente, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 0 AND (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) <= 30 Then (CP.PRIM_SALDO * -1) else 0 end ) as dias30, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 30 AND (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) <= 60 Then (CP.PRIM_SALDO * -1) else 0 end ) as dias60, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 60 AND (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) <= 90 Then (CP.PRIM_SALDO * -1) else 0 end ) as dias90, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 90 Then (CP.PRIM_SALDO * -1) else 0 end ) as mas90, "
    strSQL += " (Case when (Trunc(Sysdate) - Trunc(TO_DATE(cp.PRIM_FECHAVENCIMIENTO, 'DD/MM/YY'))) > 0 Then (CP.PRIM_SALDO * -1) else 0 end ) as totalvencido, "
    strSQL += " CP.PRIM_ORIGEN "
    strSQL += " From PROVEEDORES C ,  CP_PRIMPROVEEDORES CP  "
    strSQL += " where C.empr_empresaid  = " + str(bytEmpresa)
    strSQL += " and cp.empr_empresaid = c.empr_empresaid "
    strSQL += " and CP.PRIM_PROV_CLAVE = c.PROV_CLAVE "
    strSQL += " and cp.prim_saldo <> 0 "
    if strempresa.ref_cartera != "*":
        strSQL += " AND CP.PRIM_REFERENCIA3 LIKE ('%" + str(strempresa.ref_cartera) + "%')"
    strSQL += " Order by c.PROV_CLAVE "

    c.execute(str(strSQL)) 
    conn.close

    # Crear el DataFrame
    df_consulta = pd.DataFrame.from_records(c)
    df_consulta.columns = ['cliente', 'nombre', 'importe', 'totalcxc', 'vigente', '30','60', '90', 'mas_90', 'totalvencido', 'grupocartera']

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
        'totalvencido': 'sum'
    }).reset_index()

   # Calcular los totales para la fila "TOTAL"
    total_row = df_grouped_totals.drop(['cliente', 'grupocartera'], axis=1).sum().fillna(0)
    total_row['nombre'] = 'TOTAL CARTERA'  # Agregar el nombre "TOTAL"

    # Crear un DataFrame con la fila "TOTAL"
    df_total_row = pd.DataFrame([total_row], columns=df_grouped_totals.columns)

    # Concatenar df_grouped_totals y df_total_row
    df_final = pd.concat([df_grouped_totals, df_total_row], ignore_index=True).fillna(' ')

    # Ordenar primero por la columna 'Edad' de forma descendente y luego por 'Puntuación' de forma ascendente
    df_final = df_final.sort_values(by=['totalvencido', 'totalcxc'], ascending=[False, False])

    return df_final




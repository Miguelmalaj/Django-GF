from dashboards.utilerias import configsql
import pandas as pd

def obtiene_afluencia(bytEmpresa, bytSucursal, mes, periodo, fechahoy):

    # Crear la coneccion a sqlserver

    connsql = None
    connsql = configsql.creaconeccionsql()

    sql = connsql.cursor()

    intAfluencias =  0
    intSolicitudes =  0
    intCitas = 0
    intAprobadas =  0
    intContratos =  0

    # '******************************************************************************
    # 'AL DIA 
    strSQL = "SELECT   Afluencia = ISNULL(Sum(af_fresh_n),0), "
    strSQL = strSQL + " Citas = ISNULL(Sum(af_primera_cita_n  ),0),"
    strSQL = strSQL + " CitasAgend = ISNULL(Sum(cit_agendadas_n  ),0),"
    strSQL = strSQL + " CitasCump = ISNULL(Sum(cit_cumplidas_n  ),0),"
    strSQL = strSQL + " Solicitudes = ISNULL(Sum(sol_gmf_n  ),0),"
    strSQL = strSQL + " Demos = 0, "
    strSQL = strSQL + " Aprobadas = isnull(Sum(sol_aprobaciones_gmf_n ),0), "
    strSQL = strSQL + " Contratos = isnull(Sum(sol_contratos_comprados_n  ),0) "
    strSQL = strSQL + "FROM REPORTES_DIARIOS "
    strSQL = strSQL + " WHERE Empresa = " + str(bytEmpresa)
    strSQL = strSQL + " and Sucursal = " + str(bytSucursal)
    strSQL = strSQL + " AND id_fecha = '" + str(fechahoy) + "'"
    
    sql.execute(strSQL)

    for row in sql:
        intAfluencias =  int(row[0])
        intCitas =  int(row[1])
        intAgend =  int(row[2])
        intCumplidas =  int(row[3])
        intSolicitudes =  int(row[4])
        intAprobadas =  int(row[6])
        intContratos =  int(row[7])

    datoshoy = {
        'afluencia': intAfluencias,
        'citas': intCitas,
        'agendadas': intAgend,
        'cumplidas': intCumplidas,
        'solicitudes': intSolicitudes,
        'aprobadas': intAprobadas,
        'contratos': intContratos
    }


    # '******************************************************************************
    # 'ACUMULADOS AL DIA 
    strSQL = "SELECT   Afluencia = ISNULL(Sum(af_fresh_n),0), "
    strSQL = strSQL + " Citas = ISNULL(Sum(af_primera_cita_n  ),0),"
    strSQL = strSQL + " CitasAgend = ISNULL(Sum(cit_agendadas_n  ),0),"
    strSQL = strSQL + " CitasCump = ISNULL(Sum(cit_cumplidas_n  ),0),"
    strSQL = strSQL + " Solicitudes = ISNULL(Sum(sol_gmf_n  ),0),"
    strSQL = strSQL + " Demos = 0, "
    strSQL = strSQL + " Aprobadas = isnull(Sum(sol_aprobaciones_gmf_n ),0), "
    strSQL = strSQL + " Contratos = isnull(Sum(sol_contratos_comprados_n  ),0) "
    strSQL = strSQL + "FROM REPORTES_DIARIOS "
    strSQL = strSQL + " WHERE Empresa = " + str(bytEmpresa)
    strSQL = strSQL + " and Sucursal = " + str(bytSucursal)
    strSQL = strSQL + " AND Month (id_fecha) = " + str(mes)
    strSQL = strSQL + " AND Year (id_fecha) = " + str(periodo)	

    sql.execute(strSQL)

    for row in sql:
        intAfluencias =  int(row[0])
        intCitas =  int(row[1])
        intAgend =  int(row[2])
        intCumplidas =  int(row[3])
        intSolicitudes =  int(row[4])
        intAprobadas =  int(row[6])
        intContratos =  int(row[7])

    datosacum = {
        'afluencia': intAfluencias,
        'citas': intCitas,
        'agendadas': intAgend,
        'cumplidas': intCumplidas,
        'solicitudes': intSolicitudes,
        'aprobadas': intAprobadas,
        'contratos': intContratos
    }

    strperiodo = str(periodo) + str('0' + str(mes))[:2]
    objetivos = {
            'periodo': strperiodo,
            'afluencia': 0,
            'solicitudes':0,
            'demos': 0,
            'aprobadas': 0,
            'facturas': 0,
            'contratos': 0,
            'entregasgmf': 0,
            'entregascont': 0,
        }
    # '******************************************************************************
    # 'OBJETIVOS DEL MES
    strSQL = "SELECT  periodo, Sum(afluencia) as afluencia, Sum(solicitudes) as solicitudes, Sum(demos) as demos, Sum(aprobadas) as aprobadas, "
    strSQL = strSQL + " Sum(facturas) as facturas, Sum(contratos) as contratos, Sum(entregasgmf) as entregasgmf, sum(entregascont) as entregascont"
    strSQL = strSQL + " FROM objetivos_funnel "
    strSQL = strSQL + " WHERE Empresa = " + str(bytEmpresa)
    strSQL = strSQL + " and Sucursal = " + str(bytSucursal)
    strSQL = strSQL + " AND periodo  = " + str(strperiodo)
    strSQL = strSQL + " And vendedor = 9999"
    strSQL = strSQL + " Group by periodo"

    sql.execute(strSQL)

    connsql.close
  
    for row in sql:
        objetivos = {
            'periodo': strperiodo,
            'afluencia': int(row[1]),
            'solicitudes':int(row[2]),
            'demos':int(row[3]),
            'aprobadas': int(row[4]),
            'facturas': int(row[5]),
            'contratos': int(row[6]),
            'entregasgmf': int(row[7]),
            'entregascont': int(row[8]),
        }

    connsql.close

    return datoshoy, datosacum, objetivos

def obtiene_afluencia_vendedor(bytEmpresa, bytSucursal, mes, periodo):

    # Crear la coneccion a sqlserver

    connsql = None
    connsql = configsql.creaconeccionsql()

    sql = connsql.cursor()

    # '******************************************************************************
    # 'ACUMULADOS AL DIA 
    strSQL = "SELECT rd.numvendedor, Afluencia = ISNULL(Sum(rd.af_fresh_n +  rd.af_primera_cita_n ),0), "
    strSQL = strSQL + " Solicitudes = ISNULL(Sum(rd.sol_gmf_n  ),0), "
    strSQL = strSQL + " Aprobadas = isnull(Sum(rd.sol_aprobaciones_gmf_n ),0), "
    strSQL = strSQL + " Contratos = isnull(Sum(rd.sol_contratos_comprados_n  ),0) "
    strSQL = strSQL + "FROM REPORTES_DIARIOS  RD "
    strSQL = strSQL + " WHERE rd.Empresa = " + str(bytEmpresa)
    strSQL = strSQL + " and rd.Sucursal = " + str(bytSucursal)
    strSQL = strSQL + " AND Month (rd.id_fecha) = " + str(mes)
    strSQL = strSQL + " AND Year (rd.id_fecha) = " + str(periodo)
    strSQL = strSQL + " Group by rd.NumVendedor "
    strSQL = strSQL + " UNION ALL"
    strSQL = strSQL + " Select numvend = 0, afluencia = 0, Solicitudes = 0, Apobadas = 0, Contratos = 0 "

    sql.execute(strSQL)

    # Crear el DataFrame de las capturas de afluecia.
    funel_sql = pd.DataFrame.from_records(sql)
    if funel_sql.empty:
        datos = {
            'numvendedor':[0],
            'Afluencia':[0],
            'Solicutudes':[0],
            'Aprobadas':[0],
            'Contratos':[0]
        }
        funel_sql = pd.DataFrame(datos)

    # Dataframe para los nombres de asesores
    strSQL = " Select numvendedor, Nombre_Asesor "
    strSQL = strSQL + " From Asesores_Ventas "
    strSQL = strSQL + " Where empresa = " + str(bytEmpresa)
    strSQL = strSQL + " and Sucursal = " + str(bytSucursal)
    strSQL = strSQL + " and Activo = 'S' "
    sql.execute(strSQL)

    df_asesores = pd.DataFrame.from_records(sql)

    strperiodo = str(periodo) + ("0" + str(mes))[-2:]

    # Dataframe para los objetivos por concepto
    strSQL = " SELECT vendedor, afluencia, solicitudes, demos, aprobadas, facturas, contratos, entregasgmf = (entregasgmf + entregascont) "
    strSQL = strSQL + " FROM Objetivos_funnel "  
    strSQL = strSQL + " WHERE Empresa = " + str(bytEmpresa)
    strSQL = strSQL + " AND Sucursal = " + str(bytSucursal)
    strSQL = strSQL + " and periodo = " + str(strperiodo)
    strSQL = strSQL + " UNION ALL"
    strSQL = strSQL + " Select vendedor = 0, afluencia = 0, solicitudes = 0, demos = 0, aprobadas = 0, facturas = 0, contratos = 0, entregasgmf = 0 "
    sql.execute(strSQL)

    # Crear el DataFrame de los objetivos
    funel_objetivos = pd.DataFrame.from_records(sql)
    if funel_objetivos.empty:
        datos = {
            'vendedor':[0],
            'afluencia':[0],
            'solicutudes':[0],
            'demos':[0],
            'aprobadas':[0],
            'facturas':[0],
            'contratos':[0],
            'entregasgmf':[0]
        }
        funel_sql = pd.DataFrame(datos)

    connsql.close

    return funel_sql, funel_objetivos, df_asesores



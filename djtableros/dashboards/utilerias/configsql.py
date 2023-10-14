import pymssql
 

username = "web"
password = "webadmin"
server = "10.10.10.253"
database = "indicadores"

conn = None
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.10.10.253;DATABASE=indicadores;UID=web;PWD=webadmin'

def creaconeccionsql():
    conn = None
    
    conn = pymssql.connect(server='10.10.10.253', user='web', password='webadmin', database='indicadores')
    
    return conn

def obtiene_empresasql(bytEmpresa, bytSucursal):
    if bytEmpresa== 1:
        strempresa= "FELIX AUTOMOTORES"
    elif bytEmpresa == 2:
        strempresa= "FELIX AUTOMOTRIZ"
    elif bytEmpresa == 3:
            if bytSucursal == 1:
                strempresa= "CULIACAN ZAPATA"
            elif bytSucursal == 2:
                strempresa= "CULIACAN AEROPUERTO"
            elif bytSucursal == 3:
                strempresa= "CULIACAN FLOTILLAS"
    elif bytEmpresa == 4:
        strempresa= "NOROESTE MOTORS"
    
    return strempresa

#conexión a BD Marina
def creaconeccionsqlM():
    conn = None
    conn = pymssql.connect(server='10.0.82.10', user='web', password='webadmin', database='Marina')
    return conn

creaconeccionsql()
import cx_Oracle
from dashboards.models import empresas

encoding = "UTF-8"

conn = None

def creaconeccion(bytempresa):
    conn = None

    try:
        empresa = empresas.objects.get(empresa=bytempresa, sucursal=1 )
        conn= cx_Oracle.connect(empresa.usuario,empresa.clave_acceso,empresa.direccion_ip)
    except empresas.DoesNotExist:
        strempresa = "Empresa no encontrada"
    except cx_Oracle.Error as error:
        print(error)
    finally:
        if conn:
            return conn
        
def auntentifica_usuario(usuario, clave):
    # crear la conexion a las diferentes empresas
    conexiones = [1,3,5,7]
    for numero in conexiones:
        bytempresa = 1
        if numero == 7:
            bytempresa = 2
        conn = creaconeccion(numero)
        c = conn.cursor()
        
        strSQL = "SELECT US_IDUSUARIO, US_PASSWORD, US_NOMBRE, NVL(US_PUESTO,'NOASIGNADO') AS US_PUESTO FROM SG_USUARIO"
        strSQL = strSQL + " WHERE EMPR_EMPRESAID = " + str(bytempresa)
        strSQL = strSQL + " AND US_IDUSUARIO = '" + str(usuario.upper()) + "'"
        c.execute(str(strSQL)) 

        for datos in c:
            us_idusuario, us_password, us_nombre, us_puesto = datos

            # Validar contraseña
            if clave.upper() == us_password.upper():
                # Usuario autenticado correctamente
                usuario = {
                    'usuario': us_idusuario,
                    'nombre': us_nombre,
                    'puesto': us_puesto,
                    'empresa': bytempresa
                }
                return usuario
            
        # Cerrar la conexión después de cada empresa
        conn.close()

    # Si llegamos aquí, el usuario no fue encontrado en ninguna empresa
    return None



def obtiene_empresa(bytempresa, bytsucursal):
    try:
        strempresa = empresas.objects.get(empresa=bytempresa, sucursal=bytsucursal )
    except empresas.DoesNotExist:
        strempresa = "Empresa no encontrada"

    return strempresa


def obtiene_numero(bytEmpresa, bytSucursal):
    if bytEmpresa== 1:
        strempresa= "6682226904"    # Antonio Nieblas
    elif bytEmpresa == 2:
        strempresa= "6871420168"    # Ricardo Parra
    elif bytEmpresa == 3:
            if bytSucursal == 1:
                strempresa= "6671770000"    # Leo Felix L
            elif bytSucursal == 2:
                strempresa= "6683963164"    # Jorge Galvez
            elif bytSucursal == 3:
                strempresa= "6688613650"    # Carlos Serrano
    elif bytEmpresa == 4:
        strempresa= "6682226904"    # Antonio Nieblas
    
    return strempresa
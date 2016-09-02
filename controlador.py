#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8
__version__='0.1'
__doc__="""
Definición de métodos y utilidades para el control de la aplicación
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from decimal import *
from modelo import *
from vista import *
#import time
#import datetime
from datetime import *
import shelve
#from types import *
try:
    import cPickle as pickle
    # Utilizaremos la librería cPickle
except ImportError:
    # una implementación de Pickle más segura y rápida
    import pickle
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import FieldType
from mysql.connector import FieldFlag
FieldFlag.desc


class controlador(object):
    """   Clase controlador tiene todo los metodos de persistencia de datos
              base de datos y ficheros  del modelo
              y gestión de las señales de la vista     """
    _PERSISTENCIA = 1
    #Si 0 "shelve" si 1 cPickle
    _BBDD = 1
    # 0 sqlLite3 y 1 Mysql
    _BLOQUEO = False
    #Bloqueo si no puede añadir o cambiar datos excepto ventas
    _ESCRIBIR_DATOS_SQL_EN_DISCO = False
    _DEBUG = True
    _LOG = False

    def __init__(self, vista):
        super(controlador, self).__init__()
         #inicializamos las instancias de vista y modelo
        #if v is None:
        #    self.v = vista()
        #else:
        #    self.v = v
        #Para los Decimal() lo ponemos a dos decimales
        getcontext().prec = 4
        self.m = modelo()

        self.hoy = datetime.today()
        #.strftime(self.m.FORMATO_FECHA_0)
        self.sql_config = {
                    'user': 'tendero',
                    'password': 'changarro',
                    'host': '127.0.0.1',
                    'port': 3306,
                    'database': 'tienda',
                    'raise_on_warnings': True,
                    'charset': 'utf8',
                    'use_unicode': True,
                    'get_warnings': True,
                }
        self.funciones = [self.lee_sql_productos,
                self.lee_sql_direcciones,
                self.lee_sql_personas,
                self.lee_sql_compras,
                self.lee_sql_ventas,
                self.lee_sql_proveedoras,
                self.lee_sql_medicas,
                self.lee_sql_trabajadoras,
                self.lee_sql_clientas,
                self.lee_sql_almacenados,
                self.lee_sql_recetas,
                self.lee_sql_recetados,
                self.lee_sql_tiendas,
                self.lee_sql_albaranes,
                self.lee_sql_albaranes_compra]

        print("Cargando datos SQL:\n")
        #print(self.hoy.strftime(self.m.FORMATO_FECHA_1) + "\n")
        for i in self.funciones:
            self.sql_con(i)
            #print("cargando-" + str(i) + "\n")
        self.m.trabajadora = self.m.trabajadoras[0]
        self.m.medica = self.m.medicas[0]
        self.m.tienda = self.m.tiendas[0]
        self.m.clienta = self.m.clientas[0]
        self.m.venta = self.nueva_venta()
        self.v = vista
#

    def imprime(self, tupla):
            s = type(tupla).__name__ + '('
            for i in range(len(tupla)):
                if i == 0:
                    t = unicode(tupla[i])
                    t = t.encode("utf-8")
                    s = s + t
                else:
                    t = unicode(tupla[i])
                    t = t.encode("utf-8")
                    s = s + ', ' + t
            s = s + ')\n'
            return s

    def imprime_ticket(self):
        ruta = '/dev/usb/lp0'
        try:
            with open(ruta, 'w+') as printer:
                printer.write("\tLine 1\n")
                printer.write("Line 2\n")
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except Exception as err:
            print(err)
            print("Error escribiendo  fichero ", ruta)
        finally:
            printer.close()
            print("escribir archivo terminado" + ruta)

    def imprime_sql(self, tupla):
            s = ''
            c = ''
            #les quito el primer elemento que es un id autoincrement
            datos = tupla._asdict().values()
            columna = tupla._asdict().keys()
            datos.pop(0)
            tupla = tuple(datos)
            columna.pop(0)
            for i in range(len(tupla)):

                if type(tupla[i]) is str or unicode:
                    t = '%s'
                elif type(tupla[i]) is int or float:
                    t ='%d'
                if i == 0:
                    s = s + t
                    t = unicode(columna[i])
                    t = t.encode("utf-8")
                    c = c + t
                else:
                    s = s + ', ' + t
                    t = unicode(columna[i])
                    t = t.encode("utf-8")
                    c = c + ', ' + t

            return c, s, tupla

    def imprime_update_sql(self, tupla):
            s = ''
            dat = tupla._asdict().values()
            col = tupla._asdict().keys()
            exclusion = unicode(col[0]) + u' = ' + unicode(dat[0])
            dat.pop(0)
            tupla = tuple(dat)
            col.pop(0)
            for i in range(len(tupla)):
                if i > 0:
                    s = s + u', '
                if isinstance(tupla[i], unicode):
                    s = s + col[i] + u' = ' + u'\'' + dat[i] + u'\''
                else:
                    s = s + col[i] + u' = ' + unicode(dat[i])

            return s, exclusion

#
    def saca_tipos_columna(self, tupla):
         #creamos una Lista de tipos de columna
        # a partir de una NamedTuple
        tipos_columna = list()
        if isinstance(tupla, tuple):
            dic = tupla._asdict()
            #columnas = list(dic.keys())
            valores = list(dic.values())
            for i in valores:
                if isinstance(i, str):
                    tipos_columna.append(str)
                elif isinstance(i, unicode):
                    tipos_columna.append(str)
                elif isinstance(i, datetime):
                    tipos_columna.append(str)
                elif isinstance(i, int):
                    tipos_columna.append(int)
                else:
                    tipos_columna.append(float)
            return tipos_columna
        else:
            print("Si son None en controlador.saca_tipos_columna()")
            return None

    def saca_columnas(self, tuplas):
        #Enviamos a sacar los tipos de las filas a la primera fila
        #Primero vemos si es una lista de tuplas o una sola tupla
        if isinstance(tuplas, list):
            t0 = tuplas[0]
        else:
            t0 = tuplas
        tipos_columna = self.saca_tipos_columna(t0)
        columnas = list(t0._asdict().keys())
        return columnas, tipos_columna


    def sql_con(self, func):
        try:
            cnx = mysql.connector.connect(**self.sql_config)
            func(cnx)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Algo fue mal con el usuauario o la contraseña")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("La base de datos no existe")
            else:
                print(err)
        finally:
            cnx.close()

    def lee_sql_tabla(self, n_tabla):
        try:
            cnx = mysql.connector.connect(**self.sql_config)
            tabla = list()
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda." + n_tabla)
            #print(query)
            cursor.execute(query)
            for i in cursor:
                #p = Persona(**i._asdict())
                tabla.append(i)
                #print(imprime(i))
                #self.m.datos[n_tabla].append(i)
                #print(imprime(i))
            #self.escribir_datos_fichero(n_tabla)
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_tabla()")

        finally:
            cursor.close()
            cnx.close()
            return tabla

    def imprime_tipos_cursor(self, cursor):
    # En una consulta Mysql imprime los tipos de datos de las columnas
    # a partir d e
        for i in range(len(cursor.description)):
            print("Column {}:". format(i + 1))
            desc = cursor.description[i]
            print("  column_name = {}".format(desc[0]))
            print("  type = {} ({})".format(desc[1],
                                             FieldType.get_info(desc[1])))
            print("  null_ok = {}".format(desc[6]))
            print("  column_flags = {} ({})".format(desc[7],
                                        FieldFlag.get_info(desc[7])))

    def checa_tipos_nulos(self, dicc, description):
        #dicc es un diccionario
        #Mira si hay algún valor Null en las columnas de la Consulta MySQL
        #devuelve boolean (si hubo Nulo) y el diccionario que se paso
        # como dato con los None modificados
        r = False
        for i in range(len(description)):
            desc = description[i]
            #Si el valor de la columna es Nulo
            if dicc[desc[0]] is None:
                r = True
                if desc[1] == 3:
                    dicc[desc[0]] = 0
                elif desc[1] == 12:
                    dicc[desc[0]] = u'2000-01-01'
                elif desc[1] == 253:
                    dicc[desc[0]] = u''
                elif desc[1] == 246:
                    dicc[desc[0]] = Decimal('0.00')
                elif desc[1] == 1:
                    dicc[desc[0]] = False
        return r, dicc

    def lee_sql_productos(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)

            query = ("SELECT * FROM tienda.productos")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)

            for i in cursor:
                flag, dicc = self.checa_tipos_nulos(i._asdict(),
                                                        cursor.description)
                p = Producto(**dicc)
                if flag:
                    self.update_producto_sql(p)
                self.m.productos.append(p)
            #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_productos(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("productos")

    def lee_sql_direcciones(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.direcciones")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Direccion(**i._asdict())
                self.m.direcciones.append(p)
                #print(i._asdict())
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_direcciones(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("direcciones")

    def lee_sql_tiendas(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.tiendas")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Tienda(**i._asdict())
                self.m.tiendas.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_tiendas(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("tiendas")

    def lee_sql_personas(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.personas")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Persona(**i._asdict())
                self.m.personas.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_personas(cnx)")
        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("personas")
    #

    def lee_sql_clientas(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.clientas")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Clienta(**i._asdict())
                self.m.clientas.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_clientas(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("clientas")

    def lee_sql_trabajadoras(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.trabajadoras")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Trabajadora(**i._asdict())
                self.m.trabajadoras.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_trabajadoras(cnx)")
        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("trabajadoras")

    def lee_sql_medicas(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.medicas")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Medica(**i._asdict())
                self.m.medicas.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_medicas(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("medicas")

    def lee_sql_proveedoras(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.proveedoras")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Proveedora(**i._asdict())
                self.m.proveedoras.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_proveedoras(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("proveedoras")

    def lee_sql_compras(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.compras")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Compra(**i._asdict())
                self.m.compras.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_compras(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("compras")

    def lee_sql_ventas(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.ventas")
            cursor.execute(query)
            for i in cursor:
                p = Venta(**i._asdict())
                self.m.ventas.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_ventas(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("ventas")

    def lee_sql_almacenados(self, cnx):

        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.almacenados")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Almacenado(**i._asdict())
                self.m.almacen.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_almacenados(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("almacenados")

    def lee_sql_recetas(self, cnx):

        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.recetas")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Receta(**i._asdict())
                self.m.recetas.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_recetas(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("recetas")

    def lee_sql_recetados(self, cnx):

        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.recetados")
            cursor.execute(query)
            for i in cursor:
                p = Recetado(**i._asdict())
                self.m.recetados.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_recetados(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("recetados")

    def lee_sql_albaranes(self, cnx):

        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.albaranes")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Albaran(**i._asdict())
                self.m.albaranes.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_albaranes(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("albaranes")


    def lee_sql_albaranes_compra(self, cnx):
        try:
            cursor = cnx.cursor(named_tuple=True)
            query = ("SELECT * FROM tienda.albaranes")
            cursor.execute(query)
            #self.imprime_tipos_cursor(cursor)
            for i in cursor:
                p = Albaran(**i._asdict())
                self.m.albaranes_compra.append(p)
                #print(imprime(p))
        except Exception as err:
            print(err)
            print("Ha ocurrido una Excepcion en lee_sql_albaranes_compra(cnx)")

        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("albaranes_compra")

    def inserta_persona_sql(self, persona):
    #"""INSERT INTO `tienda`.`personas`
    #VALUES ()
    #;"""
        try:
            cnx = mysql.connector.connect(**self.sql_config)
            cursor = cnx.cursor(named_tuple=True)
            q = ("INSERT INTO tienda.personas ({0}) VALUES({1})")
            campos, valores, datos = self.imprime_sql(persona)

            q = q.format(campos, valores)
            print("consulta: ", q)
            cursor.execute(q, datos)
            cnx.commit()
            #recargamos los datos de personas
            if self._DEBUG:
                print("Recargando datos de Personas")

            self.lee_sql_personas(cnx)
            if self._DEBUG:
                print(self.m.personas[-1])
        except Exception as err:
            print(err)
            print("Ha ocurrido una excepción en inserta_persona_sql(cnx)")
            cnx.rollback()
        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("personas")
            cnx.close()

    def inserta_compras_sql(self, valor):
        try:
            cnx = mysql.connector.connect(**self.sql_config)
            cursor = cnx.cursor(named_tuple=True)
            q = ("INSERT INTO tienda.compras ({0}) VALUES({1})")
            campos, valores, datos = self.imprime_sql(valor)
            q = q.format(campos, valores)
            cursor.execute(q, datos)
            cnx.commit()
            if self._DEBUG:
                print("Recargando datos de compras")
            self.lee_sql_compras(cnx)
        except Exception as err:
            print(err)
            print("Ha ocurrido una excepción en inserta_compra_sql(cnx)")
            cnx.rollback()
        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("compras")
            cnx.close()

    def inserta_albaran_sql(self, valor):
        try:
            cnx = mysql.connector.connect(**self.sql_config)
            cursor = cnx.cursor(named_tuple=True)
            q = ("INSERT INTO tienda.albaranes ({0}) VALUES({1})")
            campos, valores, datos = self.imprime_sql(valor)
            q = q.format(campos, valores)
            cursor.execute(q, datos)
            cnx.commit()
            if self._DEBUG:
                print(q)
                print("Recargando datos de albaran")
            self.lee_sql_albaranes(cnx)
        except Exception as err:
            print(err)
            print("Ha ocurrido una excepción en inserta_albaran_sql(cnx)")
            cnx.rollback()
        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("albaran")
            cnx.close()

    def inserta_producto_sql(self, valor):
        try:
            cnx = mysql.connector.connect(**self.sql_config)
            cursor = cnx.cursor(named_tuple=True)
            q = ("INSERT INTO tienda.productos ({0}) VALUES({1})")
            datos = valor._asdict().values()
            datos.pop(0)
            datos = tuple(datos)
            campos, valores = self.imprime_sql(valor)
            q = q.format(campos, valores)
            cursor.execute(q, datos)
            cnx.commit()
            if self._DEBUG:
                print(q)
                print("Recargando datos de Productos")
            self.lee_sql_personas(cnx)
        except Exception as err:
            print(err)
            print("Ha ocurrido una excepción en inserta_producto_sql(cnx)")
            cnx.rollback()
        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("productos")
            cnx.close()

    def update_producto_sql(self, valor):
        try:
            cnx = mysql.connector.connect(**self.sql_config)
            cursor = cnx.cursor(named_tuple=True)
            q = ("UPDATE tienda.productos SET {0} WHERE {1}")
            a, exclusion = self.imprime_update_sql(valor)
            q = q.format(a, exclusion)
            cursor.execute(q)
            cnx.commit()
            if self._DEBUG:
                print(q)
                print("Actualizando datos de Productos")
            self.lee_sql_productos(cnx)
        except Exception as err:
            print(err)
            print("Ha ocurrido una excepción en update_producto_sql(cnx)")
            cnx.rollback()
        finally:
            cursor.close()
            if self._ESCRIBIR_DATOS_SQL_EN_DISCO:
                self.escribir_datos_fichero("productos")
            cnx.close()

    def leer_datos_fichero(self, que):
        """Lee de los ficheros de Respaldo"""
        try:
            #con shelve
            if self._PERSISTENCIA == 0:
                ruta = "./datos/shelve-{0}.dat".format(que)
                fichero = shelve.open(ruta)
                self.m.datos[que] = fichero[que]
            else:
               #con cPickle
                ruta = "./datos/cPickle-{0}.dat".format(que)
                fichero = file(ruta)
                self.m.datos[que] = pickle.load(fichero)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print("Error abriendo fichero ", ruta)
        finally:
            fichero.close()
            print ("leer archivos terminado")

    def escribir_datos_fichero(self, que):
        """ escribir los datos del modelo"""
        a_guardar = self.m.datos[que]
        print("Escribiendo-" + que)
        try:
            #con shelve
            if self._PERSISTENCIA == 0:
                ruta = "./datos/shelve-{0}.dat".format(que)
                print("Escribiendo datos-" + ruta)
                fichero = shelve.open(ruta)
                fichero[que] = a_guardar
            else:
                #con cPickle
                ruta = "./datos/cPickle-{0}.dat".format(que)
                print(ruta)
                fichero = file(ruta, "w+")
                pickle.dump(a_guardar, fichero)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except Exception as err:
            print(err)
            print("Error escribiendo  fichero ", ruta)
        finally:
            fichero.close()
            print("escribir archivo terminado" + ruta)
#

    def nueva_venta(self):
        #Inicializa  una nueva venta
        #
        #Primero vemos si el últimos albaran ha sido asociado a algun producto
        # si no seleccionamos su ID para el nuevo albaran de venta
        p = None
        try:
            p = self.m.albaranes[-1].productos

            if p == 1:
                id_albaran = self.m.albaranes[-1].id_albaran + 1
                print(id_albaran)
                nuevo = Albaran(id_albaran, datetime.now(),
                    self.m.clienta.id_clienta, self.m.tienda.id_tienda,
                    self.m.trabajadora.id_trabajadora,
                  0, 0, u"2000-01-01", u"venta mostrador", u"Sin anotación",
                  Decimal(0.0), Decimal(0.0))
                self.m.albaranes.append(nuevo)
                #self.inserta_albaran_sql(nuevo)
                return nuevo
            else:
                return self.m.albaranes[-1]
        except Exception as err:
            print(err)
            print("Error en controlador.nueva_venta()")
            return None

    def on_b_configuracion_clicked(self, *datos):
        print(str(datos))

#
#
    def on_venta_boton_anadir_clicked(self, *datos):
        print(str(datos))

    def on_venta_boton_quitar_clicked(self, *datos):
        print(str(datos))

    def on_venta_boton_modificar_clicked(self, *datos):
        print(str(datos))

    def on_venta_boton_guardar_clicked(self, *datos):
        print(str(datos))

    def on_venta_boton_imprimir_toggled(self, *datos):
        print(str(datos))

    def on_venta_anadir_receta(self, *datos):
        print(str(datos))

#
    def on_almacen_boton_anadir_clicked(self, *datos):
        print(str(datos))

    def on_almacen_boton_quitar_clicked(self, *datos):
        print(str(datos))

    def on_almacen_boton_modificar_clicked(self, *datos):
        print(str(datos))

    def on_almacen_boton_guardar_clicked(self, *datos):
        print(str(datos))
#
#

    def on_compras_boton_anadir_clicked(self, *datos):
        #aqui añadimos una compra
        #creamos un albaran nuevo donde el comprador es la tienda
        #comprador = self

        print(str(datos))

    def on_compras_boton_quitar_clicked(self, *datos):
        print(str(datos))

    def on_compras_boton_ver_clicked(self, *datos):
        print(str(datos))

    def on_compras_boton_modificar_clicked(self, *datos):
        print(str(datos))

    def on_compras_boton_guardar_clicked(self, *datos):
        print(str(datos))

#
#
    def on_ventas_boton_anadir_clicked(self, *datos):
        print(str(datos))

    def on_ventas_boton_quitar_clicked(self, *datos):
        print(str(datos))

    def on_ventas_boton_modificar_clicked(self, *datos):
        print(str(datos))

    def on_ventas_boton_guardar_clicked(self, *datos):
        print(str(datos))

    def on_ventas_boton_ver_clicked(self, *datos):
        print(str(datos))

#
#
    def on_productos_boton_anadir_clicked(self, *datos):
        print(str(datos))

    def on_productos_boton_quitar_clicked(self, *datos):
        print(str(datos))

    def on_productos_boton_modificar_clicked(self, *datos):
        print(str(datos))
#
#
#

    def on_activate_entry(self, *datos):
        print(str(datos))
         #Recoge los datos del Lector de Codigos y mete la informacion en el
        #albaran de venta
        #columnas = [u'id_Producto', u'Código', u'Producto', 'es_antibiótico',
        #            u'lote', u'Caducidad',
        #            u'Cantidad', u'Precio', u'IVA', u'SubTotal']
        # cantidad precio_venta iva  subtotal]
        #self.store_venta = Gtk.ListStore(int, str, str, bool, str, str, float,
        #                                    float, float, float)
        entrada = datos[0]
        cod = entrada.get_text()
        cant = datos[1].get_value_as_int()
        print(cod, cant)
        entrada.set_text("")
        datos[1].set_value(1)
        #busca Producto en almacén
        for i in self.m.productos:
            if i.codigo == cod:
                producto = i
        #Busca en el almacen todos los que tienen ese numero de producto
        for j in self.m.almacenados:
            candidatos = list()

                    #i = i.replace()
                subtotal = i.pvp * cant
                self.v.store_venta.append(i)
                print(i)
#
#

    def on_combo_changed(self, *datos):
        #print(str(datos))
        combo = datos[0]
        tree_iter = combo.get_active_iter()
        id_ = None
        if tree_iter is not None:
            model = combo.get_model()
            id_ = model[tree_iter][0]
            #
            #print("Selected: id=%s" % id_)
            #
        if 'tienda' in datos[1]:
            self.m.tienda = self.busca_id_en(id_, 'tiendas')
        elif 'clienta' in datos[1]:
            self.m.clienta = self.busca_id_en(id_, 'clientas')
        elif 'trabajadora' in datos[1]:
            p = self.busca_id_en(id_, 'trabajadoras')
            if p is not None:
                self.m.trabajadora = p
        elif 'medica' in datos[1]:
            self.m.trabajadora = self.busca_id_en(id_, 'medicas')

    def busca_id_persona(self, n_id):
        #n_id es int y busca esa id en personas
        for i in self.m.personas:
            if i.id_persona == n_id:
                return i
        #Si ha recorrido todo y no lo ha encontrado
        return None

    def busca_id_en(self, n_id, datos):
        #n_id es int y busca esa id en personas
        #print('dentro de controlador.busca_id_en()')
        #print(datos)
        for i in self.m.datos[datos]:
            dicc = i._asdict()
            keys = dicc.keys()
            if dicc[keys[0]] == n_id:
                #print(i, dicc)
                return i
        #Si ha recorrido todo y no lo ha encontrado
        #print('None en controlador.busca_id_en()')
        return None

if __name__ == "__main__":
    #NOMBRE ="compras"

    d = datetime.today()
    #print(d.timetuple())
    print(d.strftime("%Y-%m-%dT%H:%M:%S"))

    #v = vista()
    #c = controlador(v)
    #c.imprime_ticket()
    #print("Hoy es :")
    #print(c.hoy.strftime(c.m.FORMATO_FECHA_1) + "\n")
    #print("Compras:")
    #for i in c.m.compras:
    #    print(i)
    #print("Albaranes:")
    #for i in c.m.albaranes:
    #    print(i)
    #print("ventas:")
    #for i in c.m.venta:
    #    print(i)
    #c.inserta_persona_sql(c.m.TIENDA)
    #for i in c.funciones:
    #    c.sql_con(i)
    #c.imprime(c.m.PUBLICO_EN_GENERAL)
    #c.sql_con(c.lee_sql_productos)
    #c.sql_con(c.lee_sql_direcciones)
    #c.sql_con(c.lee_sql_personas)
    #c.escribir_datos_fichero("personas")
    #print(c.m.personas[0].edad)
    #t = c.lee_sql_tabla(NOMBRE)
    #k = t[0]._asdict().keys()
    #columnas = list()
    #for i in k:
    #    columnas.append(i)
    #print(columnas)
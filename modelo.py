#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__='0.1'
__doc__="""
Modelado de los tipos de Datos a usar en la aplicación
"""
__author__ = 'Juan <juan@etelsis.com>'
import collections
import time
from datetime import *
from decimal import *


def imprime(tupla):
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


class Producto(collections.namedtuple("_Producto", [
                                      "id_producto",
                                      "codigo",
                                      "nombre",
                                      "descripcion",
#                                      "ean",
                                      "fabricante",
#                                      "proveedor",
                                      "iva",
#                                      "coste",
                                      "pvp",
                                      "pvp_2",
                                      "pvp_3",
#                                      "descuento",
#                                      "moneda",
#                                      "cantidad",
#                                      "caducidad",
#                                      "lote",
                                      "antibiotico",
                                      "composicion",
                                      "presentacion"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Compra(collections.namedtuple("_Compra", ['id_compras', 'id_albaran',
     'id_producto', 'cantidad', 'precio', 'lote', 'caducidad', "iva",
      "subtotal"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Venta(collections.namedtuple("_Venta", ['id_venta', 'id_albaran',
     'id_producto', 'cantidad', 'precio', 'lote', 'caducidad', "iva",
      "subtotal"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Recetado(collections.namedtuple("_Recetado", [u'id_recetado', u'id_receta',
     u'id_producto', u'dosis', u'duracion_tratamiento', u'via_administracion'])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Almacenado(collections.namedtuple("_Almacenado", ['id_almacen',
    'id_albaran', 'id_producto', 'cantidad', 'precio_costo', 'precio_venta',
    'lote', 'caducidad', "iva"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    @property
    def caducado(self):
        hoy = date.today()
        if hoy > self.caducidad:
            return True
        else:
            return False

    def __str__(self):
        return imprime(self)


class Albaran(collections.namedtuple("_Albaran",
                                    ["id_albaran",
                                    "fecha",
                                    "id_clienta",
                                    "id_vendedora",
                                    "id_trabajadora",
                                    "id_receta",
                                    "productos",
                                    "fecha_pago",
                                    "tipo",
                                    "anotaciones",
                                     "iva",
                                     "total"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)

    def _subtotal(self, pvp, cant, iva):
        """Calcula el precio de la linea y sus impuestos
        Devuelve una TUPLA con el subtotal y aparte sus impuestos"""
        suma = 0
        impuestos = 0
        suma = (int(pvp * 100)) * int(cant)
        impuestos = ((suma * iva) / 100)
        #
        #impuestos = impuestos + suma
        return suma, impuestos

    #@property
    def total(self):
        total = 0.0
        imp = 0.0
        for i in self.productos:
            p = self._subtotal(i.pvp, i.cantidad, i.iva)
            total += p[0]
            imp += p[1]
        self.iva = imp
        self.total = total
        return total + imp, imp


class AlbaranCompra(collections.namedtuple("_AlbaranCompra",
                                    ["id_albaran_compra",
                                    "fecha",
                                    "id_proveedora",
                                    "id_trabajadora",
                                    "n_factura",
                                    "productos",
                                    "fecha_pago",
                                    "tipo",
                                    "anotaciones",
                                     "iva",
                                     "total"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)

    def _subtotal(self, pvp, cant, iva):
        """Calcula el precio de la linea y sus impuestos
        Devuelve una TUPLA con el subtotal y aparte sus impuestos"""
        suma = 0
        impuestos = 0
        suma = (int(pvp * 100)) * int(cant)
        impuestos = ((suma * iva) / 100)
        #
        #impuestos = impuestos + suma
        return suma, impuestos

    @property
    def total(self):
        total = 0.0
        imp = 0.0
        for i in self.productos:
            p = self._subtotal(i.pvp, i.cantidad, i.iva)
            total += p[0]
            imp += p[1]
        self.iva = imp
        self.total = total
        return total + imp, imp

class Direccion(collections.namedtuple("_Direccion",
 "id_direccion calle numero referencia colonia ciudad cp municipio estado pais",
                    verbose=False)):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Tienda(collections.namedtuple("_Tienda",
 "id_tienda id_persona id_direccion comentario",
                    verbose=False)):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Persona(collections.namedtuple("_Persona", ["id_persona",
                                      "nombre",
                                      "apellido1",
                                      "apellido2",
                                      "direccion",
                                      "tel",
                                      "celular",
                                      "email",
                                      "rfc",
                                      "credencial",
                                      "curp",
                                      "cedula",
                                      "direccion_fiscal",
                                      "fecha_nacimiento",
                                      "tipo"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    @property
    def edad(self):
        ahora = datetime.now()
        if self.fecha_nacimiento is not None:
            age = ahora.year - self.fecha_nacimiento.year
            return age
        else:
            return None

    @property
    def imp(self):
        clase = type(self).__name__
        s = u"{2}  {3} {4}"
        s = s.encode('utf-8')
        return s.format(clase, self.id_persona, self.nombre, self.apellido1,
                         self.apellido2, self.direccion)

    def __str__(self):
        return imprime(self)


class Medica(collections.namedtuple("_Medica", ["id_medica",
                                      'id_persona',
                                      "codigo",
                                      "especialidad",
                                      "ced_espec",
                                      "fecha_alta"])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Proveedora(collections.namedtuple("_Proveedora", ["id_proveedora",
                                      'id_persona',
                                      'comentario',
                                      'fecha_alta'])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Clienta(collections.namedtuple("_Clienta", ["id_clienta",
                                      'id_persona',
                                      'comentario',
                                      'fecha_alta'])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Trabajadora(collections.namedtuple("_Trabajadora", ['id_trabajadora',
                                      'id_persona',
                                      'codigo',
                                      'HE1',
                                      'HE2',
                                      'HS1',
                                      'HS2',
                                      'HTD',
                                      'puesto',
                                      'fecha_alta'])):
    __slots__ = ()
    _make = classmethod(tuple.__new__)

    def __str__(self):
        return imprime(self)


class Receta(collections.namedtuple("_Receta", ["id_receta",
                                      "id_usuaria",
                                      "id_medica",
                                      "n_receta",
                                      "rx",
                                      "productos",
                                      "fecha",
                                      "fecha_expendio",
                                      "original",
                                      "copia_usuaria",
                                      "copia_medica"])):
    def __str__(self):
        return imprime(self)


class modelo(object):
    # Variables GLOBALES...
    FORMATO_FECHA_0 = "%d/%m/%Y"
    FORMATO_FECHA_1 = "%a %b %d %H:%M:%S %Y"
    FORMATO_FECHA_2 = "%d-%m-%y %I:%m %p"
    FORMATO_FECHA_SQL = "%Y-%m-%d %H:%M:%S"
    FORMATO_FECHA_ISO = "%y-%m-%dT%H:%M:%S %Y"
    ESTADOS = (u'Aguascalientes', 'Baja California', u'Baja California Sur',
            u'Campeche', u'Chiapas', u'Chihuahua', u'Coahuila', u'Colima',
            u'Distrito Federal', u'Durango', u'Estado de México', u'Guanajuato',
            u'Guerrero', u'Hidalgo', u'Jalisco', u'Michoacán', u'Morelos',
            u'Nayarit', u'Nuevo León', u'Oaxaca', u'Puebla', u'Querétaro',
            u'Quintana Roo', u'San Luis Potosí', u'Sinaloa', u'Sonora',
            u'Tabasco', u'Tamaulipas', u'Tlaxcala', u'Veracruz', u'Yucatán',
                 u'Zacatecas')
    #
    #
    PUBLICO_EN_GENERAL = Persona(2, u"Público", u"en General", u"Mostrador",
                1, u"", u"", u"",
                u"XAXX010101000", u"cred", u"curp", u"ced", 1,
                date(2016, 10, 06), u"Física")
#

    def __init__(self):
        super(modelo, self).__init__()
        self.tienda = None
        self.trabajadora = None
        #Se refiera a la trabajadora actual en el mostrador
        self.medica = None
        self.venta = None
        self.clienta = None
        # Datos de la tienda se moldearan como Persona()
        self.productos = list()
        # Tupla de Productos() en almacen
        self.personas = list()
        self.medicas = list()
        self.clientas = list()
        self.trabajadoras = list()
        self.proveedoras = list()
        self.tiendas = list()
        # [] Lista de Personas() usuarias
        self.direcciones = list()
        self.ventas = list()
        #Venta actual -comprador, tipo, anotaciones
        # Tupla de Albaranes de venta
        self.compras = list()
        self.albaranes = list()
        self.albaranes_compra = list()
        self.recetas = list()
        self.recetados = list()
        self.almacenados = list()
        # Tupla de Albaranes de compra y devoluciones
        self.datos = {'productos': self.productos,
             'personas': self.personas,
             'medicas': self.medicas,
             'clientas': self.clientas,
             'trabajadoras': self.trabajadoras,
             'proveedoras': self.proveedoras,
             'direcciones': self.direcciones,
             'tiendas': self.tiendas,
             'ventas': self.ventas,
             'compras': self.compras,
             'albaranes': self.albaranes,
             'albaranes_compra': self.albaranes_compra,
             'recetas': self.recetas,
             'recetados': self.recetados,
             'almacenados': self.almacenados,
             'medica': self.medica,
             'venta': self.venta,
             'tienda': self.tienda,
             'clienta': self.clienta,
             'trabajadora': self.trabajadora
             }


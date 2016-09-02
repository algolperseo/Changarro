# -*- coding: utf-8 -*-
#
# VISTA
__version__='0.1'
__doc__="""Definición objetos utilidades la presentación en pantalla de la aplicación
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk, Gio
from controlador import *
import collections
import time
from datetime import datetime, date
from modelo import Albaran
#
# Variables GLOBALES


class vista(Gtk.Window):
    HSIZE = 1024
    VSIZE = 600
    __COLOR_OLA = '#6ccec7'
    __COLOR_LIMONCHELO = '#84d3b2'
    __COLOR_OPALO = '#bde2d1'

#
#
    def crear_button_box(self, title, widgets):
        frame = Gtk.Frame()
        frame.set_label(title)
        bbox = Gtk.HButtonBox()
        bbox.set_border_width(5)
        frame.add(bbox)
        # Set the appearance of the Button Box
        #bbox.set_layout(layout)
        bbox.set_spacing(2)
        for i in range(len(widgets)):
            bbox.add(widgets[i])
        #
        return frame

    def crea_grid(self, treeview, buttons):
        grid = Gtk.Grid()
        grid.set_column_homogeneous(False)
        grid.set_row_homogeneous(True)
        scrollable_treelist = Gtk.ScrolledWindow()
        scrollable_treelist.set_vexpand(True)
        scrollable_treelist.set_hexpand(True)
        scrollable_treelist.add(treeview)
        #attach(child, left, top, width, height)

        grid.attach(scrollable_treelist, 0, 1, 8, 10)
        #attach_next_to(child, sibling, side, width, height)
         # side = Gtk.PositionType LEFT = 0 RIGHT = 1 TOP = 2 BOTTOM = 3
        grid.attach_next_to(buttons[0], scrollable_treelist,
                             Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(buttons[1:]):
            grid.attach_next_to(button, buttons[i],
                                 Gtk.PositionType.RIGHT, 1, 1)
        if grid is None:
            print(("grid es nulo:" + grid))
        return grid

    def crea_listbox(self, titles, widgets):
        #widgets y title, son listas de titulo y widgets una para cada fila
        #Devuelve un Box Vertical con los widget ordenado por box horizontales
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        rows = list()
        #Va a contener las horizontal rows
        #1.- datos de la tabla principl botones atras siguiente
        for i in range(len(widgets)):

            if isinstance(widgets[i][0], Gtk.TreeView):
                scrollable_treelist = Gtk.ScrolledWindow()
                scrollable_treelist.set_vexpand(True)
                scrollable_treelist.set_hexpand(True)
                #scrollable_treelist.set_min_content_width(200)
                scrollable_treelist.set_min_content_height(400)
                scrollable_treelist.add(widgets[i][0])
                rows.append(scrollable_treelist)
            else:
                rows.append(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                            spacing=5))
                rows[i].add(self.crear_button_box(titles[i], widgets[i]))

            vbox.pack_start(rows[i], True, False, 0)

        if vbox is None:
            print(("listbox es nulo:" + vbox))
        return vbox


    def crea_liststore(self, tuplas):
        #DE las tuplas sacamos los tipos de columnas y los nombres
        #Devuelve un Gtk.ListStore con las tuplas y list() con los nombres
        #de las coolumnas
        columnas, tipos_columna = self.c.saca_columnas(tuplas)
        if tipos_columna is not None:
            store = Gtk.ListStore(*tipos_columna)
        #Ahora lo rellenamos de datos
        for i in tuplas:
            p = list(i._asdict().values())
            for j in range(len(p)):
                if isinstance(p[j], datetime):
                    p[j] = p[j].strftime(self.c.m.FORMATO_FECHA_SQL)
            store.append(p)
        return store, columnas

    def crea_treeview(self, tuplas):

        store, columnas = self.crea_liststore(tuplas)
        treeview = Gtk.TreeView.new_with_model(store)
        #Habilitamos la vista de las lineas
        treeview.set_enable_tree_lines(True)
        treeview.set_grid_lines(1)

        j = 0
        for i, column_title in enumerate(columnas):
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable", False)

            if j % 2 == 0:
                renderer.set_property("background", self.__COLOR_OLA)
            else:
                renderer.set_property("background", self.__COLOR_LIMONCHELO)
            j = j + 1
            renderer.set_property("background-set", False)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_resizable(True)
            column.set_sort_column_id(0)
            treeview.append_column(column)
        return treeview

#
    def crea_treeview_venta(self):
        #Store para la tabla id producto, código , nombre, es_antibiótico
        # cantidad precio_venta iva  subtotal
        columnas = [u'id_Producto', u'Código', u'Producto', 'es_antibiótico',
                    u'lote', u'Caducidad',
                    u'Cantidad', u'Precio', u'IVA', u'SubTotal']
        # cantidad precio_venta iva  subtotal]
        self.store_venta = Gtk.ListStore(int, str, str, bool, str, str, float,
                                            float, float, float)
        treeview = Gtk.TreeView.new_with_model(self.store_venta)
        #Habilitamos la vista de las lineas
        treeview.set_enable_tree_lines(True)
        treeview.set_grid_lines(1)

        j = 0
        for i, column_title in enumerate(columnas):
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable", False)

            if j % 2 == 0:
                renderer.set_property("background", "#6ccec7")
            else:
                renderer.set_property("background", "#bde2d1")
            j = j + 1
            renderer.set_property("background-set", False)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_resizable(True)
            column.set_sort_column_id(0)
            treeview.append_column(column)
        return treeview


    def inicializa_venta(self):
        widgets = list()
        #Lista de listas de widgets
        titulos = list()
        #Titulos para los frame para las listas de widgets que no sean treeview
        treeview = list()
        cabezera = list()
        #los botones de arriba de la venta
        #Label Fecha
        cabezera.append(Gtk.Label(
                self.c.m.venta.fecha.strftime("%d-%m-%Y %I:%m %p")))
        #label id_albaran
        albaran = u'Nº Albarán: {}'.format(self.c.m.venta.id_albaran)
        cabezera.append(Gtk.Label(albaran))
        #id receta + Boton añadir receta
        combo = self.crea_combo_receta()
        cabezera.append(combo)

        button = Gtk.Button.new_from_icon_name("list-add",
                                         Gtk.IconSize.SMALL_TOOLBAR)
                #button = Gtk.Button.new_with_label(nombres[i])
        button.connect("clicked", self.c.on_venta_anadir_receta,
                 u"add_receta")
        cabezera.append(button)
        # Label TOTAL + IVA
        total_iva = Gtk.Label()
        txt = u'TOTAL:  <b>{0}</b>      Iva <i>{1}</i>'.format('0.00', '0.00')
        #txt.format('0.00', '0.00')

        #txt.format(self.c.m.venta.total())#Ojo devuelve total, imp
        total_iva.set_markup(txt)
        cabezera.append(total_iva)
        #Añadimos la cabezera
        widgets.append(cabezera)
        titulos.append(u'Datos Venta')

        treeview.append(self.crea_treeview_venta())
        widgets.append(treeview)
        titulos.append(u'Venta Actual')

        nombres = ["Quitar", "Modificar", "Guardar", "Imprimir"]
        iconos = ("list-remove", "edit-redo", "document-save")
        acciones = [self.c.on_venta_boton_quitar_clicked,
                  self.c.on_venta_boton_modificar_clicked,
                  self.c.on_venta_boton_guardar_clicked,
                  self.c.on_venta_boton_imprimir_toggled]
        buttons = self.crea_botones(nombres, iconos, acciones)
        #entrada de cod
        self.entry = Gtk.Entry()
        self.entry.set_editable(True)
        icon_name = "system-search-symbolic"
        self.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
            icon_name)
        #entrada de cantidad
        self.cant = Gtk.SpinButton()
        adjustment = Gtk.Adjustment(1, 0, 100, 1, 10, 0)
        self.cant.set_adjustment(adjustment)
        policy = Gtk.SpinButtonUpdatePolicy.IF_VALID
        self.cant.set_update_policy(policy)
        self.cant.set_wrap(False)
        buttons.append(self.cant)
        self.entry.connect("activate", self.c.on_activate_entry, self.cant)
        buttons.append(self.entry)

        widgets.append(buttons)
        titulos.append(u'Acciones Venta')


        grid = self.crea_listbox(titulos, widgets)

        #Ahora los botones de arriba

        return grid

    def inicializa_almacen(self):
        self.store_almacen = Gtk.ListStore(str, str, float, float, float, str)
        treeview = Gtk.TreeView.new_with_model(self.store_almacen)
        #Habilitamos la vista de las lineas
        treeview.set_enable_tree_lines(True)
        treeview.set_grid_lines(1)
        #print(treeview.get_grid_lines())
        columnas = ["Código", "Producto", "Cantidad", "Coste", "PVP",
                    "Caducidad"]
        tam_min_columnas = (100, 400, 20, 60, 60, 60)

        for i, column_title in enumerate(columnas):
            renderer = Gtk.CellRendererText()

            renderer.set_property("editable", False)

            renderer.set_property("background", "#FFFFBE")
            renderer.set_property("background-set", True)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_min_width(tam_min_columnas[i])
            column.set_resizable(True)
            column.set_sort_column_id(0)
            treeview.append_column(column)
        nombres = ["Añadir", "Quitar", "Modificar", "Guardar"]
        iconos = ("list-add", "list-remove", "edit-redo", "document-save")
        acciones = [self.c.on_almacen_boton_anadir_clicked,
                  self.c.on_almacen_boton_quitar_clicked,
                  self.c.on_almacen_boton_modificar_clicked,
                  self.c.on_almacen_boton_guardar_clicked]
        #Ahora los botones de abajo
        return self.crea_grid(treeview,
                            self.crea_botones(nombres, iconos, acciones))

    def inicializa_compras(self):
        treeview = self.crea_treeview(self.c.m.compras)
        nombres = ["Añadir", "Quitar", "Ver", "Modificar", "Guardar"]
        iconos = ("list-add", "list-remove", "view-fullscreen", "edit-redo",
                     "document-save")
        acciones = [self.c.on_compras_boton_anadir_clicked,
                  self.c.on_compras_boton_quitar_clicked,
                  self.c.on_compras_boton_ver_clicked,
                  self.c.on_compras_boton_modificar_clicked,
                  self.c.on_compras_boton_guardar_clicked]
        #Ahora los botones de abajo
        return self.crea_grid(treeview,
                            self.crea_botones(nombres, iconos, acciones))

    def inicializa_ventas(self):
        treeview = self.crea_treeview(self.c.m.ventas)
        #Los Botones para la parte inferior
        nombres = ["Añadir", "Quitar", "Ver", "Modificar", "Guardar"]
        iconos = ("list-add", "list-remove", "view-fullscreen", "edit-redo",
                     "document-save")
        acciones = [self.c.on_ventas_boton_anadir_clicked,
                  self.c.on_ventas_boton_quitar_clicked,
                  self.c.on_ventas_boton_ver_clicked,
                  self.c.on_ventas_boton_modificar_clicked,
                  self.c.on_ventas_boton_guardar_clicked]
        return self.crea_grid(treeview,
                            self.crea_botones(nombres, iconos, acciones))

    def inicializa_productos(self):
        #crea_listmodel(self, tuplas):
        treeview = self.crea_treeview(self.c.m.productos)

        nombres = ["Añadir", "Quitar", "Modificar"]
        iconos = ("list-add", "list-remove", "view-fullscreen")
        acciones = [self.c.on_productos_boton_anadir_clicked,
                  self.c.on_productos_boton_quitar_clicked,
                  self.c.on_productos_boton_modificar_clicked]

        return self.crea_grid(treeview,
                            self.crea_botones(nombres, iconos, acciones))

    def crea_botones(self, nombres, iconos, acciones):
        #Crea una lista de botones asociados a una lista de iconos
        # y a una lista de acciones
        buttons = list()
        for i in range(len(nombres)):
            if nombres[i] is "Imprimir":
                button = Gtk.CheckButton(nombres[i])
                button.set_active(True)

                button.connect("toggled", acciones[i], "Imprimir")
            else:
                button = Gtk.Button.new_from_icon_name(iconos[i],
                                         Gtk.IconSize.SMALL_TOOLBAR)
                #button = Gtk.Button.new_with_label(nombres[i])
                button.connect("clicked", acciones[i])
            buttons.append(button)

        return buttons

    def empaqueta_box(self, box, widget):
        box.pack_end(widget, False, False, 10)

    def formatea_entry(self, datos):
        entry = Gtk.Entry()
        entry.set_editable(True)
        entry.set_text(datos)
        return entry

    def imprime_widgets(self, tupla):
        #de una namedtuple toma el nombre de la columna y crea un entry
        # con su valos para poder modificarlo
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        datos = tupla._asdict().values()
        columna = tupla._asdict().keys()
        datos.pop(0)
        columna.pop(0)
        for i in range(len(datos)):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            etiqueta = Gtk.Label(unicode(columna[i]), xalign=0)
            #self.empaqueta_box(hbox, etiqueta)
            hbox.pack_start(etiqueta, True, True, 10)
            #
            #
            if isinstance(datos[i], int):
                #hay que distiguir si es id de otro campo:
                #direccion o id_albaran, id_producto
                entry = self.formatea_entry(unicode(datos[i]))
                self.empaqueta_box(hbox, entry)
            elif isinstance(datos[i], str) or isinstance(datos[i], unicode):
                entry = self.formatea_entry(unicode(datos[i]))
                self.empaqueta_box(hbox, entry)
            elif 'datetime.datetime' in str(type(datos[i])):
                entry = self.formatea_entry(unicode(datos[i]))
                self.empaqueta_box(hbox, entry)
            elif isinstance(datos[i], bool):
                entry = CheckButton("Visible")
                self.empaqueta_box(hbox, entry)
            elif 'decimal.Decimal' in str(type(datos[i])):
                entry = self.formatea_entry(unicode(datos[i]))
                self.empaqueta_box(hbox, entry)
            row.add(hbox)
            listbox.add(row)
        return listbox

    def construye_dialog(self, tupla):
        dialog = Gtk.Dialog._new_with_buttons("Construye Dialog", self, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            #Gtk.STOCK_GO_FORWARD, Gtk.ResponseType_ACCEPT,
             Gtk.STOCK_APPLY, Gtk.ResponseType.OK))
        #self.set_default_size(150, 100)
        box = dialog.get_content_area()
        box.add(c.imprime_widgets(tupla))
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")
        dialog.destroy()

    def inicializa_ajustes(self):
        treeview = Gtk.TreeView()
        buttons = list()
        return self.crea_grid(treeview, buttons)

    def __init__(self):
        super(vista, self).__init__()
        self.set_border_width(15)
        self.set_default_size(self.HSIZE, self.VSIZE)
        self.c = controlador(self)

        #Una venta es un Albaran()
        #["numero","fecha", "comprador", "vendedor", "productos",  "fecha_pago",
        # "tipo", "anotaciones"
        #print "inicializado Controlador"
        #inicializar el header bar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Changarro 0.1"
        self.set_titlebar(hb)
        #print "inicializado el header bar"
            #boton configuracion
        b_configuracion = Gtk.Button()
        #le ponemos un icono
        #icon = Gio.ThemedIcon(name="preferences-system")
        icon = Gio.ThemedIcon(name="applications-system")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        b_configuracion.add(image)
        b_configuracion.connect("clicked", self.c.on_b_configuracion_clicked)
            #y lo ponemos atrás
        hb.pack_end(b_configuracion)

        #dialogo configuración

        #inicializar el box vertical interior
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_homogeneous(False)
        #print(vbox.get_homogeneous())
        self.add(vbox)
        #inicializar el stack switch
        self.hojas = [u"Venta",
                        u"Almacén",
                        u"Compras",
                        u"Ventas",
                        u"Productos"]
#        {"Venta": self.inicializa_venta,
#                        "Almacén": self.inicializa_almacen,
#                        "Compras": self.inicializa_compras,
#                        "Histórico": self.inicializa_historico,
#                        "Ajustes": self.inicializa_ajustes}

        # Se inicializa el Stack
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

            #inicializa Venta -el POS treelist vacio y widgets
        self.store_venta = None
        stack.add_titled(self.inicializa_venta(), u"Venta Público",
                                             u"Venta Público")
            #inicializa Almacén-Inventario.[lista de productos]
        self.store_almacen = None
        stack.add_titled(self.inicializa_almacen(), u"Almacén", u"Almacén")
            #inicializa Compras y devoluciones (Tupla de Albaranes).
        self.store_compras = None
        stack.add_titled(self.inicializa_compras(), u"Compras", u"Compras")
            #inicializa Histórico de Ventas. (Tupla de Albaranes)
        self.store_ventas = None
        stack.add_titled(self.inicializa_ventas(), u"Ventas", u"Ventas")
        self.store_productos = None
        stack.add_titled(self.inicializa_productos(), u"Productos", u"Productos")
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        vbox.pack_start(stack_switcher, True, True, 0)
        vbox.pack_start(stack, True, True, 0)
        #Ahora Los datos del pie de página
        widgets = self.crea_pie_ventana()
        self.pie_ventana = self.crear_button_box("Datos", widgets)
        vbox.pack_start(self.pie_ventana, True, True, 0)

    def crea_pie_ventana(self):
        #creamos los combo_box de tienda, trabajadoras
        widgets = list()
        tupla = ('tiendas', 'trabajadoras', 'clientas', 'medicas')
        for i in tupla:
            store, cols = self.crea_liststore(self.c.m.datos[i])
            listmodel = Gtk.ListStore(int, str)
            for j in range(len(store)):
                #la columna 0 es la id de la tabla
                # y la columna 1 es la id_persona
                persona = self.c.busca_id_persona(store[j][1])
                nombre = unicode(persona.imp)
                p = [store[j][0], nombre]
                listmodel.append(p)
            combo = Gtk.ComboBox.new_with_model(listmodel)
            renderer_text = Gtk.CellRendererText()
            combo.pack_start(renderer_text, True)
            combo.add_attribute(renderer_text, "text", 1)
            combo.connect("changed", self.c.on_combo_changed, i[:-1])
            combo.set_active(0)
            combo.set_entry_text_column(0)
            widgets.append(Gtk.Label(i[:-1]))
            widgets.append(combo)
        return widgets

    def crea_combo_receta(self):
        try :
            store, cols = self.crea_liststore(self.c.m.datos['recetas'])
            listmodel = Gtk.ListStore(int, str, str)
            #Lismodel id_receta, nombreclienta, nombre doctora
            for j in range(len(store)):
                #la columna 0 es la id de la receta
                # y la columna 1 es la id_clienta
                # y la columna 2 es la id_doctora
                #
                clienta = self.c.busca_id_en(store[j][1], 'clientas')
                doctora = self.c.busca_id_en(store[j][2], 'doctoras')
                clienta = self.c.busca_id_persona(clienta[1])
                nombre_clienta = unicode(clienta.imp)
                doctora = self.c.busca_id_persona(doctora[1])
                nombre_doctora = unicode(clienta.imp)
                p = [store[j][0], nombre_clienta, nombre_doctora]
                listmodel.append(p)

            combo = Gtk.ComboBox.new_with_model(listmodel)
            renderer_text = Gtk.CellRendererText()
            combo.pack_start(renderer_text, True)
            combo.add_attribute(renderer_text, "text", 1)
            combo.connect("changed", self.c.on_combo_changed, i[:-1])
            combo.set_active(0)
            combo.set_entry_text_column(0)
            return combo
        except Exception as err:
            print(err)
            print("Error en vista.crea_combo_receta(self)")
            receta = u'Nº Receta: {}'.format(self.c.m.venta.id_receta)
            return Gtk.Label(receta)




if __name__ == "__main__":
    win = vista()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
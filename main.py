# =============================================================================
# main.py — Ventana principal y coordinador de la aplicación
# Investigación de Operaciones — Método de la Esquina Noroeste
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
import random
from decimal import Decimal

# Módulos propios
from logica import (
    ProblemaTransporte, validar_problema, balancear_problema,
    resolver_esquina_noroeste, ResultadoCosto, _fmt, formatear_numero,
    resolver_optimo_transporte,
    EJEMPLO_PREDEFINIDO, generar_problema_aleatorio,
    problema_a_dict, dict_a_problema
)
from estilos import COLOR, FUENTE, configurar_estilos, crear_scrollframe, tooltip
from widgets_tabla import TablaCostos, TablaAsignaciones


# =============================================================================
# Ventana de Ayuda
# =============================================================================

class VentanaAyuda(tk.Toplevel):
    """Ventana independiente con instrucciones completas del programa."""

    TEXTO = """
╔══════════════════════════════════════════════════════════╗
║    AYUDA — Método de la Esquina Noroeste                 ║
║    Investigación de Operaciones                          ║
╚══════════════════════════════════════════════════════════╝

¿QUÉ ES UN PROBLEMA DE TRANSPORTE?
───────────────────────────────────
Un problema de transporte busca determinar la cantidad óptima de
productos que deben enviarse desde varios orígenes (fábricas,
almacenes) hacia varios destinos (tiendas, clientes), minimizando
el costo total de transporte, respetando las capacidades de oferta
de cada origen y las necesidades de demanda de cada destino.

¿QUÉ ES EL MÉTODO DE LA ESQUINA NOROESTE?
──────────────────────────────────────────
Es un método sencillo para obtener una solución básica factible
INICIAL. Parte de la esquina superior-izquierda (noroeste) de la
tabla y asigna la mayor cantidad posible, avanzando hacia la derecha
o hacia abajo según se agoten la oferta o la demanda.

IMPORTANTE: El método de la esquina noroeste NO garantiza que la
solución sea de costo mínimo. Es un punto de partida. Para obtener
la solución óptima se necesitan métodos adicionales como MODI o
la regla de la escalera.

CÓMO USAR EL PROGRAMA
──────────────────────
PASO 1 — Configurar el problema
  En la pestaña "Configuración", escriba el número de orígenes
  y destinos y haga clic en "Crear tabla".

PASO 2 — Ingresar datos
  En la tabla que aparece en "Datos del problema":
  • Escriba los costos en cada celda de la matriz.
  • Escriba la oferta de cada origen en la columna derecha.
  • Escriba la demanda de cada destino en la fila inferior.
  • Puede cambiar los nombres de orígenes y destinos directamente.

PASO 3 — Verificar balance
  El programa verifica automáticamente si la oferta total
  es igual a la demanda total.
  • Si están balanceadas: puede resolver directamente.
  • Si no están balanceadas: use "Balancear automáticamente".

PASO 4 — Resolver
  Haga clic en "Resolver ejercicio" para aplicar el método.
  El programa mostrará:
  • El procedimiento paso a paso con explicaciones.
  • La tabla de asignaciones finales.
  • El cálculo del costo total.

NAVEGACIÓN PASO A PASO
  Use los botones "Paso anterior" y "Paso siguiente" para
  recorrer cada operación del algoritmo.
  Use "Mostrar solución completa" para ver todo de una vez.

GUARDAR Y ABRIR
  • "Guardar ejercicio": guarda los datos en un archivo .json
  • "Abrir ejercicio": carga un ejercicio guardado previamente
  • "Exportar resultados": guarda los resultados en .txt o .csv

FUNCIONES ADICIONALES
  • "Ejemplo automático": carga un ejercicio de ejemplo
  • "Datos aleatorios": genera un problema con valores aleatorios
  • "Limpiar tabla": borra todos los datos (pide confirmación)
  • "Reiniciar ejercicio": vuelve al estado inicial

COLORES DE LA TABLA
───────────────────
  🟡 Amarillo claro  → celda en proceso actualmente
  🟢 Verde claro     → celda con asignación (positiva)
  ⬜ Gris claro      → fila/columna ya satisfecha
  🟣 Morado claro    → elemento ficticio (para balance)
  🔵 Azul            → encabezados (orígenes/destinos)

PREGUNTAS FRECUENTES
────────────────────
P: ¿Puedo usar decimales?
R: Sí. El programa acepta cualquier número decimal válido.

P: ¿Qué es la degeneración?
R: Ocurre cuando el número de asignaciones es menor que m+n-1,
   donde m = orígenes y n = destinos. El programa lo detecta
   y lo informa claramente.

P: ¿Los costos pueden ser cero o negativos?
R: Los costos pueden ser cero. Los costos negativos se permiten
   cuando el usuario lo necesita (para modelar ciertos problemas).

P: ¿Qué pasa con los orígenes/destinos ficticios?
R: Son artificiales, no representan flujo real. Las cantidades
   asignadas a ficticios son "inventario sin distribuir" o
   "demanda no atendida" según el caso.
"""

    def __init__(self, padre):
        super().__init__(padre)
        self.title('Ayuda — Método de la Esquina Noroeste')
        self.geometry('680x600')
        self.resizable(True, True)
        self.configure(bg=COLOR['fondo'])
        self.grab_set()

        # Encabezado
        tk.Label(
            self, text='Ayuda del programa',
            font=FUENTE['titulo'],
            fg=COLOR['texto_encabezado'],
            bg=COLOR['primario']
        ).pack(fill='x', pady=0)

        # Área de texto con scroll
        frame = tk.Frame(self, bg=COLOR['fondo'])
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        scroll = ttk.Scrollbar(frame)
        scroll.pack(side='right', fill='y')
        texto = tk.Text(
            frame, font=FUENTE['mono'], bg=COLOR['panel'],
            fg=COLOR['texto'], relief='flat',
            yscrollcommand=scroll.set, wrap='word',
            state='normal', padx=10, pady=10
        )
        texto.insert('1.0', self.TEXTO.strip())
        texto.config(state='disabled')
        texto.pack(fill='both', expand=True)
        scroll.config(command=texto.yview)

        ttk.Button(
            self, text='Cerrar', style='Primario.TButton',
            command=self.destroy
        ).pack(pady=8)


# =============================================================================
# Ventana principal
# =============================================================================

class AplicacionTransporte(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title('Método de la Esquina Noroeste — Investigación de Operaciones')

        # Habilitar soporte DPI en Windows para evitar interfaz borrosa o mal escalada
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        # Dimensiones calculadas responsivamente según la pantalla del usuario
        try:
            ancho_pantalla = self.winfo_screenwidth()
            alto_pantalla = self.winfo_screenheight()
            ancho_inicial = min(1280, max(950, int(ancho_pantalla * 0.92)))
            alto_inicial = min(820, max(600, int(alto_pantalla * 0.88)))
            self.geometry(f'{ancho_inicial}x{alto_inicial}+30+20')
        except Exception:
            self.geometry('1100x700')

        self.minsize(850, 520)
        self.configure(bg=COLOR['fondo'])

        # En Windows, abrir maximizada para que la interfaz se vea completa y perfecta
        try:
            self.state('zoomed')
        except Exception:
            pass

        # Configurar estilos ttk
        configurar_estilos(self)

        # ── Estado interno ────────────────────────────────────────────────
        self._num_origenes = tk.IntVar(value=3)
        self._num_destinos = tk.IntVar(value=4)
        self._nombre_ejercicio = tk.StringVar(value='')
        self._tabla_costos_widget = None   # TablaCostos editable
        self._problema_original = None     # ProblemaTransporte validado
        self._problema_balanceado = None   # ProblemaTransporte balanceado
        self._tipo_ajuste = 'ninguno'
        self._ajuste_valor = Decimal('0')
        self._asignaciones = None
        self._pasos = []
        self._paso_actual = -1
        self._es_degenerado = False
        self._resultado_costo = None
        self._indices_ficticios = {}
        self._costo_optimo = None
        self._asignaciones_optimas = None

        # Construir interfaz
        self._construir_interfaz()
        self._crear_tabla(inicial=True)

    # =========================================================================
    # Construcción de la interfaz
    # =========================================================================

    def _construir_interfaz(self):
        """Crea la barra de herramientas, pestañas y barra de estado."""
        self._construir_barra_herramientas()
        self._construir_notebook()
        self._construir_barra_estado()

    # ── Barra de herramientas superior ────────────────────────────────────

    def _construir_barra_herramientas(self):
        barra = tk.Frame(self, bg=COLOR['primario'], pady=6)
        barra.pack(fill='x', side='top')

        # Título
        tk.Label(
            barra,
            text='🚚  Método de la Esquina Noroeste',
            font=FUENTE['titulo'],
            fg='white', bg=COLOR['primario']
        ).pack(side='left', padx=16)

        # Botones de archivo (derecha)
        btn_frame = tk.Frame(barra, bg=COLOR['primario'])
        btn_frame.pack(side='right', padx=10)

        btns_archivo = [
            ('💾 Guardar', self._guardar_ejercicio),
            ('📂 Abrir',   self._abrir_ejercicio),
            ('📤 Exportar', self._exportar_resultados),
            ('❓ Ayuda',   self._mostrar_ayuda),
        ]
        for texto, cmd in btns_archivo:
            b = tk.Button(
                btn_frame, text=texto,
                font=FUENTE['pequena'],
                fg='white', bg=COLOR['primario_oscuro'],
                activeforeground='white', activebackground=COLOR['primario'],
                relief='flat', padx=8, pady=4, cursor='hand2',
                command=cmd
            )
            b.pack(side='left', padx=3)

    # ── Notebook (pestañas principales) ───────────────────────────────────

    def _construir_notebook(self):
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill='both', expand=True, padx=8, pady=(4, 0))

        # Pestaña 1: Configuración + Datos
        self._tab_datos = tk.Frame(self._notebook, bg=COLOR['fondo'])
        self._notebook.add(self._tab_datos, text='  📋 Datos del problema  ')

        # Pestaña 2: Balance
        self._tab_balance = tk.Frame(self._notebook, bg=COLOR['fondo'])
        self._notebook.add(self._tab_balance, text='  ⚖ Balance  ')

        # Pestaña 3: Resolución
        self._tab_resolucion = tk.Frame(self._notebook, bg=COLOR['fondo'])
        self._notebook.add(self._tab_resolucion, text='  🔢 Resolución paso a paso  ')

        # Pestaña 4: Resultados
        self._tab_resultados = tk.Frame(self._notebook, bg=COLOR['fondo'])
        self._notebook.add(self._tab_resultados, text='  📊 Resultados y costo  ')

        self._construir_tab_datos()
        self._construir_tab_balance()
        self._construir_tab_resolucion()
        self._construir_tab_resultados()

    # ── Barra de estado inferior ───────────────────────────────────────────

    def _construir_barra_estado(self):
        barra = tk.Frame(self, bg=COLOR['primario_oscuro'], height=28)
        barra.pack(fill='x', side='bottom')
        self._lbl_estado = tk.Label(
            barra, text='Listo.',
            font=FUENTE['pequena'],
            fg='white', bg=COLOR['primario_oscuro'],
            anchor='w', padx=10
        )
        self._lbl_estado.pack(side='left', fill='x', expand=True)
        tk.Label(
            barra,
            text='Investigación de Operaciones — Esquina Noroeste',
            font=FUENTE['pequena'],
            fg=COLOR['primario_claro'], bg=COLOR['primario_oscuro'],
            padx=10
        ).pack(side='right')

    def _set_estado(self, msg):
        self._lbl_estado.config(text=msg)

    # =========================================================================
    # Pestaña 1: Datos del problema
    # =========================================================================

    def _construir_tab_datos(self):
        tab = self._tab_datos

        # ── Panel de configuración (izquierda, con scroll para cualquier resolución) ──
        frame_izq_ext, panel_izq = crear_scrollframe(tab, bg=COLOR['panel'])
        frame_izq_ext.config(width=270)
        frame_izq_ext.pack(side='left', fill='y', padx=(8, 4), pady=8)

        lbl_tit_cfg = tk.Label(
            panel_izq, text=' ① Configuración ',
            font=FUENTE['seccion'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario'], padx=8, pady=4
        )
        lbl_tit_cfg.pack(fill='x', padx=4, pady=(4, 6))

        # Nombre del ejercicio
        tk.Label(panel_izq, text='Nombre del ejercicio:',
                 font=FUENTE['pequena'], bg=COLOR['panel'],
                 fg=COLOR['texto_secundario']).pack(anchor='w', padx=8, pady=(4, 0))
        tk.Entry(panel_izq, textvariable=self._nombre_ejercicio,
                 font=FUENTE['normal'], width=22,
                 relief='groove').pack(padx=8, pady=2, fill='x')

        ttk.Separator(panel_izq, orient='horizontal').pack(fill='x', pady=6, padx=8)

        # Dimensiones compactas
        tk.Label(panel_izq, text='Dimensiones de la matriz:',
                 font=FUENTE['seccion'], bg=COLOR['panel'],
                 fg=COLOR['primario']).pack(anchor='w', padx=8, pady=(2, 4))

        frame_dims = tk.Frame(panel_izq, bg=COLOR['panel'])
        frame_dims.pack(padx=8, fill='x')

        tk.Label(frame_dims, text='Orígenes:', font=FUENTE['normal'],
                 bg=COLOR['panel']).grid(row=0, column=0, sticky='w', pady=2)
        ttk.Spinbox(
            frame_dims, from_=1, to=20, width=5,
            textvariable=self._num_origenes, font=FUENTE['normal']
        ).grid(row=0, column=1, padx=4, pady=2)

        tk.Label(frame_dims, text='Destinos:', font=FUENTE['normal'],
                 bg=COLOR['panel']).grid(row=1, column=0, sticky='w', pady=2)
        ttk.Spinbox(
            frame_dims, from_=1, to=20, width=5,
            textvariable=self._num_destinos, font=FUENTE['normal']
        ).grid(row=1, column=1, padx=4, pady=2)

        ttk.Button(
            panel_izq, text='🔧 Crear / Ajustar tabla',
            style='Primario.TButton',
            command=self._crear_tabla
        ).pack(padx=8, pady=(6, 4), fill='x')

        # Botones rápidos para +/- filas y columnas
        frame_filas_cols = tk.Frame(panel_izq, bg=COLOR['panel'])
        frame_filas_cols.pack(padx=8, pady=2, fill='x')

        ttk.Button(frame_filas_cols, text='+ Origen', style='Secundario.TButton',
                   command=self._agregar_origen).grid(row=0, column=0, padx=2, pady=2, sticky='ew')
        ttk.Button(frame_filas_cols, text='- Origen', style='Secundario.TButton',
                   command=self._eliminar_origen).grid(row=0, column=1, padx=2, pady=2, sticky='ew')
        ttk.Button(frame_filas_cols, text='+ Destino', style='Secundario.TButton',
                   command=self._agregar_destino).grid(row=1, column=0, padx=2, pady=2, sticky='ew')
        ttk.Button(frame_filas_cols, text='- Destino', style='Secundario.TButton',
                   command=self._eliminar_destino).grid(row=1, column=1, padx=2, pady=2, sticky='ew')
        frame_filas_cols.columnconfigure(0, weight=1)
        frame_filas_cols.columnconfigure(1, weight=1)

        ttk.Separator(panel_izq, orient='horizontal').pack(fill='x', pady=6, padx=8)

        # Botones de acción principales en el panel
        tk.Label(panel_izq, text='Acciones principales:',
                 font=FUENTE['seccion'], bg=COLOR['panel'],
                 fg=COLOR['primario']).pack(anchor='w', padx=8, pady=(2, 4))

        ttk.Button(
            panel_izq, text='▶ Resolver Esquina Noroeste',
            style='Exito.TButton',
            command=self._resolver_ejercicio
        ).pack(padx=8, pady=3, fill='x')

        ttk.Button(
            panel_izq, text='⚖ Verificar Balance',
            style='Primario.TButton',
            command=lambda: self._notebook.select(self._tab_balance)
                            or self._verificar_y_pasar_balance()
        ).pack(padx=8, pady=3, fill='x')

        ttk.Separator(panel_izq, orient='horizontal').pack(fill='x', pady=6, padx=8)

        # Herramientas
        tk.Label(panel_izq, text='Herramientas útiles:',
                 font=FUENTE['pequena'], bg=COLOR['panel'],
                 fg=COLOR['texto_secundario']).pack(anchor='w', padx=8)

        ttk.Button(
            panel_izq, text='⭐ Cargar Ejemplo',
            style='Secundario.TButton', command=self._cargar_ejemplo
        ).pack(padx=8, pady=2, fill='x')

        ttk.Button(
            panel_izq, text='🎲 Datos Aleatorios',
            style='Secundario.TButton', command=self._generar_aleatorio
        ).pack(padx=8, pady=2, fill='x')

        ttk.Button(
            panel_izq, text='🧹 Limpiar Tabla',
            style='Peligro.TButton', command=self._limpiar_tabla
        ).pack(padx=8, pady=(2, 10), fill='x')

        # ── Panel de la tabla (derecha) ──────────────────────────────────
        panel_tabla = tk.LabelFrame(
            tab, text=' ② Matriz de Costos, Ofertas y Demandas ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_tabla.pack(side='left', fill='both', expand=True,
                         padx=(4, 8), pady=8, ipadx=4, ipady=4)

        # ── BARRA DE ACCIONES RÁPIDAS SUPERIOR (Siempre visible) ──────────
        barra_rapida = tk.Frame(panel_tabla, bg=COLOR['fondo'], pady=4)
        barra_rapida.pack(fill='x', padx=6, pady=(2, 6))

        tk.Label(barra_rapida, text='⚡ Acciones rápidas:', font=FUENTE['seccion'],
                 bg=COLOR['fondo'], fg=COLOR['primario']).pack(side='left', padx=6)

        ttk.Button(
            barra_rapida, text='▶ RESOLVER EJERCICIO',
            style='Exito.TButton', command=self._resolver_ejercicio
        ).pack(side='left', padx=4)

        ttk.Button(
            barra_rapida, text='⚖ Balancear',
            style='Primario.TButton',
            command=lambda: self._notebook.select(self._tab_balance)
                            or self._verificar_y_pasar_balance()
        ).pack(side='left', padx=4)

        ttk.Button(
            barra_rapida, text='⭐ Ejemplo',
            style='Secundario.TButton', command=self._cargar_ejemplo
        ).pack(side='left', padx=4)

        ttk.Button(
            barra_rapida, text='🎲 Aleatorio',
            style='Secundario.TButton', command=self._generar_aleatorio
        ).pack(side='left', padx=4)

        ttk.Button(
            barra_rapida, text='🧹 Limpiar',
            style='Peligro.TButton', command=self._limpiar_tabla
        ).pack(side='right', padx=6)

        frame_ext, self._frame_tabla_interior = crear_scrollframe(panel_tabla, bg=COLOR['panel'])
        frame_ext.pack(fill='both', expand=True, padx=4, pady=4)
        self._frame_tabla_contenedor = self._frame_tabla_interior

    # =========================================================================
    # Pestaña 2: Balance
    # =========================================================================

    def _construir_tab_balance(self):
        tab = self._tab_balance

        # Encabezado
        tk.Label(
            tab, text='③ Verificación y Balance del Problema',
            font=FUENTE['titulo'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario']
        ).pack(fill='x', pady=0)

        contenido, _ = crear_scrollframe(tab, bg=COLOR['fondo'])
        contenido.pack(fill='both', expand=True)
        self._frame_balance_scroll = _

        # El contenido real se construye en _mostrar_balance()
        tk.Label(
            self._frame_balance_scroll,
            text='Ingrese los datos en la pestaña "Datos del problema"\n'
                 'y luego haga clic en "Verificar balance".',
            font=FUENTE['normal'],
            fg=COLOR['texto_secundario'],
            bg=COLOR['fondo']
        ).pack(pady=40)

    def _actualizar_tab_balance(self):
        """Reconstruye el contenido de la pestaña de balance."""
        for w in self._frame_balance_scroll.winfo_children():
            w.destroy()

        p_orig = self._problema_original
        p_bal = self._problema_balanceado
        tipo = self._tipo_ajuste
        val = self._ajuste_valor

        scroll_frame = self._frame_balance_scroll

        # ── Resumen del balance ───────────────────────────────────────────
        panel_info = tk.LabelFrame(
            scroll_frame,
            text=' Análisis del balance ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_info.pack(fill='x', padx=16, pady=(12, 6))

        # Totales
        grid_info = tk.Frame(panel_info, bg=COLOR['panel'])
        grid_info.pack(padx=12, pady=8)

        datos_resumen = [
            ('Total de oferta:', formatear_numero(p_orig.oferta_total())),
            ('Total de demanda:', formatear_numero(p_orig.demanda_total())),
            ('Diferencia (Oferta − Demanda):', formatear_numero(p_orig.diferencia())),
        ]
        for fila, (etiq, val_str) in enumerate(datos_resumen):
            tk.Label(grid_info, text=etiq, font=FUENTE['normal'],
                     fg=COLOR['texto_secundario'], bg=COLOR['panel'],
                     anchor='e').grid(row=fila, column=0, sticky='e', padx=(0, 8), pady=2)
            tk.Label(grid_info, text=val_str, font=FUENTE['subtitulo'],
                     fg=COLOR['primario'], bg=COLOR['panel'],
                     anchor='w').grid(row=fila, column=1, sticky='w', pady=2)

        # Estado
        if tipo == 'ninguno':
            color_est = COLOR['exito']
            icon_est = '✔'
            msg_est = ('El problema está BALANCEADO. La oferta total es igual a la demanda total.\n'
                       'Se puede aplicar directamente el Método de la Esquina Noroeste.')
        elif tipo == 'destino_ficticio':
            color_est = COLOR['advertencia']
            icon_est = '⚠'
            msg_est = (f'El problema NO está balanceado. La OFERTA supera a la demanda en '
                       f'{_fmt(val)} unidades.\n'
                       f'Se agregó un "Destino Ficticio" con demanda = {_fmt(val)} y costos = 0.\n'
                       f'Las unidades asignadas al destino ficticio representan exceso de inventario\n'
                       f'que no será distribuido a ningún cliente real.')
        else:
            color_est = COLOR['advertencia']
            icon_est = '⚠'
            msg_est = (f'El problema NO está balanceado. La DEMANDA supera a la oferta en '
                       f'{_fmt(val)} unidades.\n'
                       f'Se agregó un "Origen Ficticio" con oferta = {_fmt(val)} y costos = 0.\n'
                       f'Las unidades asignadas desde el origen ficticio representan demanda\n'
                       f'que no podrá ser atendida con la capacidad actual.')

        frame_estado = tk.Frame(panel_info, bg=color_est, padx=8, pady=6)
        frame_estado.pack(fill='x', padx=12, pady=(0, 10))
        tk.Label(
            frame_estado, text=f'{icon_est}  {msg_est}',
            font=FUENTE['normal'], fg='white' if tipo != 'ninguno' else 'white',
            bg=color_est, anchor='w', justify='left', wraplength=700
        ).pack(anchor='w')

        # ── Tabla original ────────────────────────────────────────────────
        panel_orig = tk.LabelFrame(
            scroll_frame, text=' Tabla original ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_orig.pack(fill='x', padx=16, pady=6)
        self._mostrar_tabla_estatica(panel_orig, p_orig)

        # ── Tabla balanceada (si hubo ajuste) ─────────────────────────────
        if tipo != 'ninguno':
            panel_bal = tk.LabelFrame(
                scroll_frame,
                text=f' Tabla balanceada (con {p_bal.origenes[-1] if tipo == "origen_ficticio" else p_bal.destinos[-1]}) ',
                font=FUENTE['seccion'], fg=COLOR['primario'],
                bg=COLOR['panel'], relief='groove', bd=1
            )
            panel_bal.pack(fill='x', padx=16, pady=6)
            self._mostrar_tabla_estatica(panel_bal, p_bal,
                                          indice_ficticio_orig=len(p_bal.origenes) - 1 if tipo == 'origen_ficticio' else None,
                                          indice_ficticio_dest=len(p_bal.destinos) - 1 if tipo == 'destino_ficticio' else None)

        # ── Botones ───────────────────────────────────────────────────────
        frame_btns = tk.Frame(scroll_frame, bg=COLOR['fondo'])
        frame_btns.pack(pady=12)
        ttk.Button(
            frame_btns, text='▶ Continuar → Resolver ejercicio',
            style='Exito.TButton',
            command=self._resolver_ejercicio
        ).pack(side='left', padx=6)
        ttk.Button(
            frame_btns, text='← Volver a los datos',
            style='Secundario.TButton',
            command=lambda: self._notebook.select(self._tab_datos)
        ).pack(side='left', padx=6)

    def _mostrar_tabla_estatica(self, padre, problema,
                                 indice_ficticio_orig=None,
                                 indice_ficticio_dest=None):
        """Muestra la tabla de costos como solo lectura en el padre indicado."""
        from decimal import Decimal as D
        p = problema
        m = p.num_origenes()
        n = p.num_destinos()

        frame = tk.Frame(padre, bg=COLOR['panel'])
        frame.pack(padx=8, pady=8, anchor='w')

        # Encabezado
        tk.Label(frame, text='', bg=COLOR['celda_encabezado'],
                 width=12, relief='flat').grid(row=0, column=0, padx=1, pady=1, sticky='nsew')
        for j, dest in enumerate(p.destinos):
            es_fict = (j == indice_ficticio_dest)
            bg = COLOR['celda_ficticia'] if es_fict else COLOR['celda_encabezado']
            fg = COLOR['texto'] if es_fict else COLOR['texto_encabezado']
            tk.Label(frame, text=dest, font=FUENTE['celda'],
                     fg=fg, bg=bg, width=9, relief='flat', anchor='center'
                     ).grid(row=0, column=j + 1, padx=1, pady=1, sticky='nsew')
        tk.Label(frame, text='Oferta', font=FUENTE['celda'],
                 fg=COLOR['texto_encabezado'], bg=COLOR['primario_oscuro'],
                 width=8, relief='flat', anchor='center'
                 ).grid(row=0, column=n + 1, padx=1, pady=1, sticky='nsew')

        for i in range(m):
            es_fict_o = (i == indice_ficticio_orig)
            bg_orig = COLOR['celda_ficticia'] if es_fict_o else COLOR['celda_encabezado']
            fg_orig = COLOR['texto'] if es_fict_o else COLOR['texto_encabezado']
            tk.Label(frame, text=p.origenes[i], font=FUENTE['celda'],
                     fg=fg_orig, bg=bg_orig, width=12, relief='flat', anchor='w', padx=4
                     ).grid(row=i + 1, column=0, padx=1, pady=1, sticky='nsew')
            for j in range(n):
                es_fict_c = (i == indice_ficticio_orig or j == indice_ficticio_dest)
                bg_c = COLOR['celda_agotada'] if es_fict_c else COLOR['celda_normal']
                costo = formatear_numero(p.costos[i][j])
                tk.Label(frame, text=costo, font=FUENTE['celda_num'],
                         fg=COLOR['texto'], bg=bg_c,
                         width=8, relief='groove', anchor='center'
                         ).grid(row=i + 1, column=j + 1, padx=1, pady=1, sticky='nsew')
            tk.Label(frame, text=formatear_numero(p.ofertas[i]),
                     font=FUENTE['celda_num'],
                     fg='white', bg=COLOR['primario_oscuro'],
                     width=8, relief='flat', anchor='center'
                     ).grid(row=i + 1, column=n + 1, padx=1, pady=1, sticky='nsew')

        tk.Label(frame, text='Demanda', font=FUENTE['celda'],
                 fg=COLOR['texto_encabezado'], bg=COLOR['primario_oscuro'],
                 width=12, relief='flat', anchor='center'
                 ).grid(row=m + 1, column=0, padx=1, pady=1, sticky='nsew')
        for j in range(n):
            es_fict = (j == indice_ficticio_dest)
            bg_d = COLOR['celda_ficticia'] if es_fict else COLOR['primario_oscuro']
            tk.Label(frame, text=formatear_numero(p.demandas[j]),
                     font=FUENTE['celda_num'],
                     fg='white', bg=bg_d,
                     width=8, relief='flat', anchor='center'
                     ).grid(row=m + 1, column=j + 1, padx=1, pady=1, sticky='nsew')

    # =========================================================================
    # Pestaña 3: Resolución paso a paso
    # =========================================================================

    def _construir_tab_resolucion(self):
        tab = self._tab_resolucion

        tk.Label(
            tab, text='④ Resolución — Método de la Esquina Noroeste',
            font=FUENTE['titulo'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario']
        ).pack(fill='x')

        # Panel de controles
        panel_ctrl = tk.Frame(tab, bg=COLOR['panel'], pady=6)
        panel_ctrl.pack(fill='x', padx=8, pady=(6, 0))

        self._lbl_paso_info = tk.Label(
            panel_ctrl,
            text='Presione "Resolver ejercicio" para comenzar.',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], anchor='w'
        )
        self._lbl_paso_info.pack(side='left', padx=10)

        btn_frame = tk.Frame(panel_ctrl, bg=COLOR['panel'])
        btn_frame.pack(side='right', padx=8)

        self._btn_paso_ant = ttk.Button(
            btn_frame, text='◀ Paso anterior',
            style='Secundario.TButton',
            command=self._paso_anterior
        )
        self._btn_paso_ant.pack(side='left', padx=3)

        self._btn_paso_sig = ttk.Button(
            btn_frame, text='Paso siguiente ▶',
            style='Primario.TButton',
            command=self._paso_siguiente
        )
        self._btn_paso_sig.pack(side='left', padx=3)

        self._btn_solucion = ttk.Button(
            btn_frame, text='⚡ Mostrar solución completa',
            style='Advertencia.TButton',
            command=self._mostrar_solucion_completa
        )
        self._btn_solucion.pack(side='left', padx=3)

        ttk.Separator(tab, orient='horizontal').pack(fill='x', pady=2)

        # Área principal dividida: tabla (arriba) + texto explicativo (abajo)
        panel_principal = tk.PanedWindow(
            tab, orient='vertical',
            bg=COLOR['fondo'], sashwidth=6,
            sashrelief='flat', sashpad=2
        )
        panel_principal.pack(fill='both', expand=True, padx=8, pady=4)

        # Panel tabla (arriba)
        self._frame_tabla_paso = tk.LabelFrame(
            panel_principal, text=' Tabla en proceso ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_principal.add(self._frame_tabla_paso, minsize=180)

        # Contenedor con scroll para la tabla de asignaciones
        frame_scroll_tabla, self._frame_tabla_paso_int = crear_scrollframe(
            self._frame_tabla_paso, bg=COLOR['panel']
        )
        frame_scroll_tabla.pack(fill='both', expand=True, padx=4, pady=4)

        # Panel texto (abajo)
        frame_texto = tk.LabelFrame(
            panel_principal, text=' Explicación del paso ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_principal.add(frame_texto, minsize=120)

        scroll_txt = ttk.Scrollbar(frame_texto)
        scroll_txt.pack(side='right', fill='y')
        self._txt_paso = tk.Text(
            frame_texto, font=FUENTE['mono'],
            bg=COLOR['resultado_fondo'],
            fg=COLOR['texto'], relief='flat',
            yscrollcommand=scroll_txt.set,
            state='disabled', wrap='word',
            padx=10, pady=8, height=8
        )
        self._txt_paso.pack(fill='both', expand=True)
        scroll_txt.config(command=self._txt_paso.yview)

    def _actualizar_vista_paso(self, indice):
        """Actualiza la tabla y el texto explicativo para el paso dado."""
        if not self._pasos or indice < 0 or indice >= len(self._pasos):
            return

        paso = self._pasos[indice]

        # Actualizar etiqueta de progreso
        total = len(self._pasos)
        self._lbl_paso_info.config(
            text=f'Paso {paso.numero} de {total}  —  '
                 f'Celda: {paso.nombre_origen} → {paso.nombre_destino}'
        )

        # Actualizar botones
        self._btn_paso_ant.config(state='normal' if indice > 0 else 'disabled')
        self._btn_paso_sig.config(state='normal' if indice < total - 1 else 'disabled')

        # Limpiar frame de tabla
        for w in self._frame_tabla_paso_int.winfo_children():
            w.destroy()

        # Mostrar tabla con asignaciones acumuladas hasta este paso
        TablaAsignaciones(
            self._frame_tabla_paso_int,
            problema=self._problema_balanceado,
            asignaciones=self._asignaciones,
            indices_ficticios=self._indices_ficticios,
            celda_activa=(paso.fila, paso.columna),
            asignaciones_acumuladas=paso.asignaciones_acumuladas
        ).pack(anchor='nw', padx=4, pady=4)

        # Actualizar texto explicativo
        self._txt_paso.config(state='normal')
        self._txt_paso.delete('1.0', 'end')
        self._txt_paso.insert('1.0', paso.descripcion())
        if paso.es_ultimo:
            self._txt_paso.insert('end', '\n\n✔ ¡PROCESO COMPLETADO! Todas las ofertas y '
                                          'demandas han sido satisfechas.\n'
                                          'Vea los resultados en la pestaña "Resultados y costo".')
        if self._es_degenerado:
            self._txt_paso.insert('end',
                '\n\n⚠ DEGENERACIÓN DETECTADA: El número de asignaciones es menor\n'
                f'que m+n-1 = {self._problema_balanceado.num_origenes()}+'
                f'{self._problema_balanceado.num_destinos()}-1 = '
                f'{self._problema_balanceado.num_origenes()+self._problema_balanceado.num_destinos()-1}.\n'
                'Esto puede ocurrir cuando la oferta y la demanda de una celda se\n'
                'agotan simultáneamente (empate). En la práctica, se puede asignar\n'
                'un valor de ε (épsilon, muy pequeño) a una celda adicional para\n'
                'completar la base factible.'
            )
        self._txt_paso.config(state='disabled')

    def _paso_siguiente(self):
        if self._paso_actual < len(self._pasos) - 1:
            self._paso_actual += 1
            self._actualizar_vista_paso(self._paso_actual)

    def _paso_anterior(self):
        if self._paso_actual > 0:
            self._paso_actual -= 1
            self._actualizar_vista_paso(self._paso_actual)

    def _mostrar_solucion_completa(self):
        """Salta directamente al último paso."""
        if self._pasos:
            self._paso_actual = len(self._pasos) - 1
            self._actualizar_vista_paso(self._paso_actual)
            self._notebook.select(self._tab_resultados)

    # =========================================================================
    # Pestaña 4: Resultados y costo total
    # =========================================================================

    def _construir_tab_resultados(self):
        tab = self._tab_resultados

        tk.Label(
            tab, text='⑤ Resultados y Costo Total',
            font=FUENTE['titulo'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario']
        ).pack(fill='x')

        # Scroll general
        frame_ext, self._frame_resultados_int = crear_scrollframe(tab, bg=COLOR['fondo'])
        frame_ext.pack(fill='both', expand=True, padx=8, pady=4)

    def _actualizar_tab_resultados(self):
        """Reconstruye la pestaña de resultados con los datos actuales."""
        for w in self._frame_resultados_int.winfo_children():
            w.destroy()

        frame = self._frame_resultados_int
        rc = self._resultado_costo
        p_bal = self._problema_balanceado

        # ── Tabla de asignaciones finales ─────────────────────────────────
        panel_tabla = tk.LabelFrame(
            frame, text=' Tabla final de asignaciones ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_tabla.pack(fill='x', padx=12, pady=(10, 6))

        TablaAsignaciones(
            panel_tabla,
            problema=p_bal,
            asignaciones=self._asignaciones,
            indices_ficticios=self._indices_ficticios
        ).pack(anchor='nw', padx=8, pady=8)

        # ── Desglose de asignaciones ──────────────────────────────────────
        panel_asg = tk.LabelFrame(
            frame, text=' Desglose de asignaciones ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_asg.pack(fill='x', padx=12, pady=6)

        for linea in rc.desglose_lineas():
            tk.Label(
                panel_asg, text=linea,
                font=FUENTE['mono'],
                fg=COLOR['texto'], bg=COLOR['panel'],
                anchor='w'
            ).pack(anchor='w', padx=12, pady=1)

        # Separar ficticias si existen
        fict_orig = self._indices_ficticios.get('origen')
        fict_dest = self._indices_ficticios.get('destino')
        ficticas = [t for t in rc.terminos if
                    (fict_orig is not None and p_bal.origenes[rc.terminos.index(t) if False else 0] == p_bal.origenes[-1])
                    or (fict_dest is not None)]
        # Nota simplificada
        if self._tipo_ajuste != 'ninguno':
            texto_fict = ''
            if self._tipo_ajuste == 'destino_ficticio':
                texto_fict = (f'Nota: Las unidades asignadas al "{p_bal.destinos[-1]}" '
                              f'representan exceso de oferta ({_fmt(self._ajuste_valor)} unidades) '
                              f'que no se distribuye a ningún destino real.')
            else:
                texto_fict = (f'Nota: Las unidades asignadas desde el "{p_bal.origenes[-1]}" '
                              f'representan demanda no cubierta ({_fmt(self._ajuste_valor)} unidades) '
                              f'que no puede ser atendida con la capacidad actual.')
            tk.Label(
                panel_asg, text=texto_fict,
                font=FUENTE['pequena'],
                fg=COLOR['advertencia'], bg=COLOR['advertencia_claro'],
                anchor='w', wraplength=700, justify='left',
                padx=8, pady=4
            ).pack(fill='x', padx=12, pady=6)

        # ── Cálculo del costo ─────────────────────────────────────────────
        panel_costo = tk.LabelFrame(
            frame, text=' Cálculo del costo total ',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], relief='groove', bd=1
        )
        panel_costo.pack(fill='x', padx=12, pady=6)

        tk.Text(
            panel_costo, font=FUENTE['mono_grande'],
            bg=COLOR['resultado_fondo'],
            fg=COLOR['texto'], relief='flat',
            state='normal', wrap='word',
            padx=12, pady=8, height=6
        ).pack(fill='x', padx=8, pady=6)

        # Insertar fórmula
        txt_costo = panel_costo.winfo_children()[-1]
        txt_costo.insert('1.0', rc.formula_desarrollada())
        txt_costo.config(state='disabled')

        # Resultado destacado
        frame_total = tk.Frame(panel_costo, bg=COLOR['primario_claro'],
                               padx=16, pady=10)
        frame_total.pack(fill='x', padx=8, pady=(0, 8))
        tk.Label(
            frame_total, text='Costo total de transporte:',
            font=FUENTE['subtitulo'], fg=COLOR['primario'],
            bg=COLOR['primario_claro']
        ).pack(side='left')
        tk.Label(
            frame_total, text=f'  {_fmt(rc.costo_total)}',
            font=('Segoe UI', 18, 'bold'),
            fg=COLOR['primario_oscuro'],
            bg=COLOR['primario_claro']
        ).pack(side='left')

        tk.Label(
            frame_total, text=f'  (cantidad total transportada: {_fmt(rc.cantidad_total)} unidades)',
            font=FUENTE['pequena'], fg=COLOR['texto_secundario'],
            bg=COLOR['primario_claro']
        ).pack(side='left', padx=12)

        # ── Comparación con la Solución Óptima (Costo Mínimo Real) ─────────
        if self._costo_optimo is not None:
            panel_opt = tk.LabelFrame(
                frame, text=' 🎯 Evaluación de Optimalidad (Costo Mínimo Real) ',
                font=FUENTE['seccion'], fg=COLOR['primario'],
                bg=COLOR['panel'], relief='groove', bd=1
            )
            panel_opt.pack(fill='x', padx=12, pady=6)

            costo_no = rc.costo_total
            costo_opt = self._costo_optimo

            grid_opt = tk.Frame(panel_opt, bg=COLOR['panel'])
            grid_opt.pack(fill='x', padx=12, pady=6)

            tk.Label(grid_opt, text='Costo Esquina Noroeste:', font=FUENTE['subtitulo'],
                     bg=COLOR['panel'], fg=COLOR['texto']).grid(row=0, column=0, sticky='w', padx=6, pady=2)
            tk.Label(grid_opt, text=f'${formatear_numero(costo_no)}', font=FUENTE['subtitulo'],
                     bg=COLOR['panel'], fg=COLOR['primario']).grid(row=0, column=1, sticky='w', padx=6, pady=2)

            tk.Label(grid_opt, text='Costo Mínimo Óptimo:', font=FUENTE['subtitulo'],
                     bg=COLOR['panel'], fg=COLOR['texto']).grid(row=1, column=0, sticky='w', padx=6, pady=2)
            tk.Label(grid_opt, text=f'${formatear_numero(costo_opt)}', font=FUENTE['subtitulo'],
                     bg=COLOR['panel'], fg=COLOR['exito']).grid(row=1, column=1, sticky='w', padx=6, pady=2)

            if costo_no == costo_opt:
                msg_opt = ('✔ ¡ESPECTACULAR! La solución obtenida por la Esquina Noroeste\n'
                           'es exactamente la SOLUCIÓN ÓPTIMA DE COSTO MÍNIMO.\n'
                           'No existe ninguna otra asignación en este problema que tenga un costo menor.')
                color_fondo_opt = COLOR['exito_claro']
                color_texto_opt = '#155724'
            else:
                dif_ahorro = costo_no - costo_opt
                pct = ((dif_ahorro / costo_no) * 100) if costo_no > 0 else 0
                msg_opt = (f'💡 DIAGNÓSTICO DE OPTIMALIDAD:\n'
                           f'La solución de la Esquina Noroeste es factible pero no es la de costo mínimo.\n'
                           f'La solución óptima reduce el costo a ${formatear_numero(costo_opt)}, '
                           f'ahorrando ${formatear_numero(dif_ahorro)} ({pct:.1f}% de reducción).')
                color_fondo_opt = COLOR['advertencia_claro']
                color_texto_opt = '#856404'

            frame_msg_opt = tk.Frame(panel_opt, bg=color_fondo_opt, padx=10, pady=8)
            frame_msg_opt.pack(fill='x', padx=12, pady=(0, 6))
            tk.Label(frame_msg_opt, text=msg_opt, font=FUENTE['normal'],
                     bg=color_fondo_opt, fg=color_texto_opt, justify='left', anchor='w').pack(side='left')

            if self._asignaciones_optimas is not None and costo_no != costo_opt:
                ttk.Button(
                    panel_opt, text='🔍 Ver Tabla de Asignaciones Óptimas (Costo Mínimo)',
                    style='Primario.TButton',
                    command=self._mostrar_modal_solucion_optima
                ).pack(padx=12, pady=(0, 8), anchor='w')

        # ── Advertencia importante ────────────────────────────────────────
        panel_adv = tk.Frame(frame, bg=COLOR['advertencia_claro'],
                              padx=12, pady=8)
        panel_adv.pack(fill='x', padx=12, pady=6)
        tk.Label(
            panel_adv,
            text='ℹ Recordatorio Teórico: El Método de la Esquina Noroeste obtiene una\n'
                 'solución básica factible inicial siguiendo estrictamente la posición de las celdas.\n'
                 'Para asegurar la solución óptima, compare siempre con el panel de optimalidad superior.',
            font=FUENTE['normal'],
            fg=COLOR['texto'], bg=COLOR['advertencia_claro'],
            anchor='w', justify='left'
        ).pack(anchor='w')

        # ── Degeneración ──────────────────────────────────────────────────
        if self._es_degenerado:
            m = p_bal.num_origenes()
            n = p_bal.num_destinos()
            panel_deg = tk.Frame(frame, bg=COLOR['peligro_claro'], padx=12, pady=8)
            panel_deg.pack(fill='x', padx=12, pady=6)
            tk.Label(
                panel_deg,
                text=f'⚠ DEGENERACIÓN: El número de asignaciones es menor que m+n-1 '
                     f'({m}+{n}-1={m+n-1}).\n'
                     f'Esto ocurre cuando la oferta y la demanda de una misma celda se\n'
                     f'agotan simultáneamente. Se puede agregar una variable básica de\n'
                     f'valor ε ≈ 0 para completar la solución básica si es necesario.',
                font=FUENTE['normal'],
                fg=COLOR['peligro'], bg=COLOR['peligro_claro'],
                anchor='w', justify='left'
            ).pack(anchor='w')

        # ── Botones de acción ─────────────────────────────────────────────
        frame_btns = tk.Frame(frame, bg=COLOR['fondo'])
        frame_btns.pack(pady=12)
        ttk.Button(
            frame_btns, text='📤 Exportar resultados',
            style='Primario.TButton',
            command=self._exportar_resultados
        ).pack(side='left', padx=6)
        ttk.Button(
            frame_btns, text='🔄 Reiniciar ejercicio',
            style='Advertencia.TButton',
            command=self._reiniciar
        ).pack(side='left', padx=6)
        ttk.Button(
            frame_btns, text='◀ Ver pasos',
            style='Secundario.TButton',
            command=lambda: self._notebook.select(self._tab_resolucion)
        ).pack(side='left', padx=6)

    def _mostrar_modal_solucion_optima(self):
        """Abre una ventana emergente moderna mostrando la asignación óptima de costo mínimo."""
        if self._asignaciones_optimas is None or self._problema_balanceado is None:
            return

        modal = tk.Toplevel(self)
        modal.title('Solución Óptima de Costo Mínimo')
        modal.geometry('780x520')
        modal.minsize(600, 400)
        modal.configure(bg=COLOR['fondo'])
        modal.grab_set()

        # Encabezado
        barra_tit = tk.Frame(modal, bg=COLOR['primario'], pady=10)
        barra_tit.pack(fill='x')
        tk.Label(
            barra_tit, text='🎯 Asignación Óptima de Costo Mínimo',
            font=FUENTE['titulo'], fg='white', bg=COLOR['primario']
        ).pack()

        # Resumen de comparación
        frame_res = tk.Frame(modal, bg=COLOR['panel'], pady=8, padx=16)
        frame_res.pack(fill='x', padx=12, pady=(10, 6))

        costo_no = self._resultado_costo.costo_total
        costo_opt = self._costo_optimo
        ahorro = costo_no - costo_opt
        pct = ((ahorro / costo_no) * 100) if costo_no > 0 else 0

        tk.Label(
            frame_res,
            text=f'Costo Esquina Noroeste: ${formatear_numero(costo_no)}   →   '
                 f'Costo Óptimo: ${formatear_numero(costo_opt)}   |   '
                 f'Ahorro posible: ${formatear_numero(ahorro)} ({pct:.1f}%)',
            font=FUENTE['subtitulo'], fg=COLOR['exito'], bg=COLOR['panel']
        ).pack()

        # Contenedor con scroll para la tabla óptima
        frame_ext, frame_int = crear_scrollframe(modal, bg=COLOR['fondo'])
        frame_ext.pack(fill='both', expand=True, padx=12, pady=6)

        TablaAsignaciones(
            frame_int,
            problema=self._problema_balanceado,
            asignaciones=self._asignaciones_optimas,
            indices_ficticios=self._indices_ficticios
        ).pack(anchor='nw', padx=8, pady=8)

        # Botón cerrar
        ttk.Button(modal, text='Cerrar', style='Primario.TButton', command=modal.destroy).pack(pady=8)

    # =========================================================================
    # Lógica de negocio — Creación y modificación de tabla
    # =========================================================================

    def _crear_tabla(self, inicial=False):
        """Crea o recrea la tabla de datos con las dimensiones actuales."""
        try:
            m = int(self._num_origenes.get())
            n = int(self._num_destinos.get())
        except Exception:
            messagebox.showerror('Error', 'Ingrese números válidos para orígenes y destinos.')
            return

        if m < 1 or n < 1:
            messagebox.showerror('Error', 'Debe haber al menos 1 origen y 1 destino.')
            return
        if m > 20 or n > 20:
            if not messagebox.askyesno('Tabla grande',
                                        f'Va a crear una tabla de {m}×{n}. '
                                        f'¿Desea continuar?'):
                return

        # Guardar datos actuales antes de recrear
        datos_prev = self._obtener_datos_actuales()

        # Eliminar tabla anterior
        for widget in self._frame_tabla_contenedor.winfo_children():
            widget.destroy()

        # Nombres por defecto
        origenes = [f'Origen {i+1}' for i in range(m)]
        destinos  = [f'Destino {j+1}' for j in range(n)]

        # Restaurar nombres anteriores si existen
        if datos_prev:
            for i in range(min(m, len(datos_prev.get('origenes', [])))):
                origenes[i] = datos_prev['origenes'][i]
            for j in range(min(n, len(datos_prev.get('destinos', [])))):
                destinos[j] = datos_prev['destinos'][j]

        self._tabla_costos_widget = TablaCostos(
            self._frame_tabla_contenedor,
            origenes=origenes,
            destinos=destinos
        )
        self._tabla_costos_widget.pack(anchor='nw', padx=8, pady=8)

        # Restaurar datos anteriores
        if datos_prev and not inicial:
            costos_prev = datos_prev.get('costos', [])
            ofertas_prev = datos_prev.get('ofertas', [])
            demandas_prev = datos_prev.get('demandas', [])
            if costos_prev:
                self._tabla_costos_widget.cargar_datos(
                    costos_prev, ofertas_prev, demandas_prev
                )

        self._set_estado(f'Tabla creada: {m} orígenes × {n} destinos.')

    def _obtener_datos_actuales(self):
        """Retorna un dict con los datos actuales de la tabla o None."""
        if not self._tabla_costos_widget:
            return None
        costos, ofertas, demandas, orig, dest = self._tabla_costos_widget.obtener_datos()
        return {'costos': costos, 'ofertas': ofertas, 'demandas': demandas,
                'origenes': orig, 'destinos': dest}

    def _agregar_origen(self):
        self._num_origenes.set(self._num_origenes.get() + 1)
        self._crear_tabla()

    def _eliminar_origen(self):
        if self._num_origenes.get() <= 1:
            messagebox.showwarning('Aviso', 'Debe haber al menos 1 origen.')
            return
        self._num_origenes.set(self._num_origenes.get() - 1)
        self._crear_tabla()

    def _agregar_destino(self):
        self._num_destinos.set(self._num_destinos.get() + 1)
        self._crear_tabla()

    def _eliminar_destino(self):
        if self._num_destinos.get() <= 1:
            messagebox.showwarning('Aviso', 'Debe haber al menos 1 destino.')
            return
        self._num_destinos.set(self._num_destinos.get() - 1)
        self._crear_tabla()

    def _limpiar_tabla(self):
        if not messagebox.askyesno(
            'Confirmar limpieza',
            '¿Desea borrar todos los datos de la tabla?\nEsta acción no se puede deshacer.'
        ):
            return
        if self._tabla_costos_widget:
            self._tabla_costos_widget.limpiar()
        self._set_estado('Tabla limpiada.')

    def _reiniciar(self):
        if not messagebox.askyesno(
            'Confirmar reinicio',
            '¿Desea reiniciar completamente el ejercicio?\nSe perderán todos los datos y resultados.'
        ):
            return
        self._problema_original = None
        self._problema_balanceado = None
        self._asignaciones = None
        self._pasos = []
        self._paso_actual = -1
        self._resultado_costo = None
        self._limpiar_tabla()
        self._notebook.select(self._tab_datos)
        self._set_estado('Ejercicio reiniciado.')

    # =========================================================================
    # Lógica de negocio — Validación y balance
    # =========================================================================

    def _verificar_y_pasar_balance(self):
        """Valida datos, balancea y muestra la pestaña de balance."""
        problema, errores = self._validar_datos()
        if errores:
            return

        p_bal, tipo, val = balancear_problema(problema)
        self._problema_original = problema
        self._problema_balanceado = p_bal
        self._tipo_ajuste = tipo
        self._ajuste_valor = val

        # Índices ficticios para colorear
        self._indices_ficticios = {}
        if tipo == 'origen_ficticio':
            self._indices_ficticios['origen'] = p_bal.num_origenes() - 1
        elif tipo == 'destino_ficticio':
            self._indices_ficticios['destino'] = p_bal.num_destinos() - 1

        self._actualizar_tab_balance()
        self._notebook.select(self._tab_balance)
        self._set_estado('Balance verificado.')

    def _validar_datos(self):
        """Lee y valida los datos de la tabla. Muestra errores al usuario."""
        if not self._tabla_costos_widget:
            messagebox.showerror('Error', 'Primero cree una tabla.')
            return None, ['Sin tabla']

        costos_txt, ofertas_txt, demandas_txt, orig, dest = \
            self._tabla_costos_widget.obtener_datos()

        problema, errores = validar_problema(
            orig, dest, costos_txt, ofertas_txt, demandas_txt
        )

        if errores:
            mensaje = 'Se encontraron los siguientes errores:\n\n' + '\n'.join(
                f'  • {e}' for e in errores
            )
            messagebox.showerror('Datos incorrectos', mensaje)
            return None, errores

        return problema, None

    # =========================================================================
    # Lógica de negocio — Resolución
    # =========================================================================

    def _resolver_ejercicio(self):
        """Valida, balancea y resuelve el ejercicio completo."""
        problema, errores = self._validar_datos()
        if errores:
            return

        # Balancear
        p_bal, tipo, val = balancear_problema(problema)
        self._problema_original = problema
        self._problema_balanceado = p_bal
        self._tipo_ajuste = tipo
        self._ajuste_valor = val

        self._indices_ficticios = {}
        if tipo == 'origen_ficticio':
            self._indices_ficticios['origen'] = p_bal.num_origenes() - 1
        elif tipo == 'destino_ficticio':
            self._indices_ficticios['destino'] = p_bal.num_destinos() - 1

        # Resolver
        asignaciones, pasos, es_degenerado = resolver_esquina_noroeste(p_bal)
        self._asignaciones = asignaciones
        self._pasos = pasos
        self._es_degenerado = es_degenerado

        # Calcular costo
        self._resultado_costo = ResultadoCosto(
            asignaciones,
            p_bal.costos,
            p_bal.origenes,
            p_bal.destinos
        )

        # Calcular también solución óptima global de costo mínimo
        try:
            asig_opt, costo_opt = resolver_optimo_transporte(p_bal)
            self._asignaciones_optimas = asig_opt
            self._costo_optimo = costo_opt
        except Exception:
            self._asignaciones_optimas = None
            self._costo_optimo = None

        # Iniciar en el paso 0
        self._paso_actual = 0
        self._actualizar_vista_paso(0)

        # Actualizar pestañas de balance y resultados
        self._actualizar_tab_balance()
        self._actualizar_tab_resultados()

        # Ir a la pestaña de resolución
        self._notebook.select(self._tab_resolucion)
        self._set_estado(
            f'Ejercicio resuelto: {len(pasos)} pasos, '
            f'costo total = {_fmt(self._resultado_costo.costo_total)}.'
            + (' ⚠ Solución degenerada.' if es_degenerado else '')
        )

    # =========================================================================
    # Herramientas adicionales
    # =========================================================================

    def _cargar_ejemplo(self):
        """Carga el ejercicio de ejemplo predefinido."""
        datos = EJEMPLO_PREDEFINIDO
        m = len(datos['origenes'])
        n = len(datos['destinos'])
        self._num_origenes.set(m)
        self._num_destinos.set(n)
        self._crear_tabla(inicial=True)
        self._tabla_costos_widget.cargar_datos(
            datos['costos'],
            datos['ofertas'],
            datos['demandas'],
            origenes=datos['origenes'],
            destinos=datos['destinos']
        )
        self._nombre_ejercicio.set('Ejemplo predefinido')
        self._set_estado('Ejemplo cargado. Revise los datos y resuelva el ejercicio.')

    def _generar_aleatorio(self):
        """Diálogo para generar datos aleatorios."""
        dialogo = tk.Toplevel(self)
        dialogo.title('Generar datos aleatorios')
        dialogo.geometry('380x320')
        dialogo.resizable(False, False)
        dialogo.configure(bg=COLOR['panel'])
        dialogo.grab_set()

        tk.Label(dialogo, text='Generador de datos aleatorios',
                 font=FUENTE['subtitulo'], fg=COLOR['primario'],
                 bg=COLOR['panel']).pack(pady=10)

        campos = tk.Frame(dialogo, bg=COLOR['panel'])
        campos.pack(padx=20, fill='x')

        vars_config = {}
        configuracion = [
            ('Orígenes:', 'origenes', 3, 1, 10),
            ('Destinos:', 'destinos', 4, 1, 10),
            ('Costo mínimo:', 'cost_min', 1, 0, 99),
            ('Costo máximo:', 'cost_max', 20, 1, 999),
            ('Oferta mínima:', 'of_min', 10, 1, 999),
            ('Oferta máxima:', 'of_max', 100, 1, 9999),
            ('Demanda mínima:', 'dem_min', 10, 1, 999),
            ('Demanda máxima:', 'dem_max', 100, 1, 9999),
        ]
        for fila, (etiq, clave, default, desde, hasta) in enumerate(configuracion):
            tk.Label(campos, text=etiq, font=FUENTE['normal'],
                     bg=COLOR['panel'], anchor='e', width=18
                     ).grid(row=fila, column=0, sticky='e', pady=3, padx=(0, 6))
            var = tk.IntVar(value=default)
            vars_config[clave] = var
            ttk.Spinbox(campos, from_=desde, to=hasta, textvariable=var,
                        width=8).grid(row=fila, column=1, sticky='w')

        var_bal = tk.BooleanVar(value=True)
        tk.Checkbutton(
            dialogo, text='Problema balanceado automáticamente',
            variable=var_bal, font=FUENTE['normal'],
            bg=COLOR['panel'], fg=COLOR['texto']
        ).pack(pady=6)

        def generar():
            try:
                m = vars_config['origenes'].get()
                n = vars_config['destinos'].get()
                datos = generar_problema_aleatorio(
                    m, n,
                    rango_costos=(vars_config['cost_min'].get(), max(vars_config['cost_min'].get() + 1, vars_config['cost_max'].get())),
                    rango_ofertas=(vars_config['of_min'].get(), max(vars_config['of_min'].get() + 1, vars_config['of_max'].get())),
                    rango_demandas=(vars_config['dem_min'].get(), max(vars_config['dem_min'].get() + 1, vars_config['dem_max'].get())),
                    balanceado=var_bal.get()
                )
                self._num_origenes.set(m)
                self._num_destinos.set(n)
                self._crear_tabla(inicial=True)
                self._tabla_costos_widget.cargar_datos(
                    datos['costos'], datos['ofertas'], datos['demandas'],
                    origenes=datos['origenes'], destinos=datos['destinos']
                )
                dialogo.destroy()
                self._set_estado(f'Datos aleatorios generados: {m}×{n}.')
            except Exception as e:
                messagebox.showerror('Error', str(e), parent=dialogo)

        ttk.Button(dialogo, text='🎲 Generar', style='Primario.TButton',
                   command=generar).pack(pady=10)
        ttk.Button(dialogo, text='Cancelar', style='Secundario.TButton',
                   command=dialogo.destroy).pack()

    # =========================================================================
    # Guardar, abrir, exportar
    # =========================================================================

    def _guardar_ejercicio(self):
        if not self._tabla_costos_widget:
            messagebox.showwarning('Aviso', 'No hay datos que guardar.')
            return

        datos = self._obtener_datos_actuales()
        problema, errores = validar_problema(
            datos['origenes'], datos['destinos'],
            datos['costos'], datos['ofertas'], datos['demandas']
        )
        if errores:
            if not messagebox.askyesno(
                'Datos incompletos',
                'La tabla tiene datos incompletos o inválidos.\n'
                '¿Desea guardar de todas formas los datos actuales (incluyendo vacíos)?'
            ):
                return
            # Guardar en formato raw
            archivo = filedialog.asksaveasfilename(
                defaultextension='.json',
                filetypes=[('Ejercicio de transporte', '*.json'), ('Todos', '*.*')],
                title='Guardar ejercicio'
            )
            if not archivo:
                return
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump({
                    'nombre': self._nombre_ejercicio.get(),
                    'origenes': datos['origenes'],
                    'destinos': datos['destinos'],
                    'costos': datos['costos'],
                    'ofertas': datos['ofertas'],
                    'demandas': datos['demandas'],
                    'raw': True
                }, f, ensure_ascii=False, indent=2)
            self._set_estado(f'Ejercicio guardado en: {os.path.basename(archivo)}')
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('Ejercicio de transporte', '*.json'), ('Todos', '*.*')],
            title='Guardar ejercicio',
            initialfile=self._nombre_ejercicio.get() or 'ejercicio_transporte'
        )
        if not archivo:
            return

        d = problema_a_dict(problema, nombre=self._nombre_ejercicio.get())
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

        self._set_estado(f'Ejercicio guardado: {os.path.basename(archivo)}')
        messagebox.showinfo('Guardado', f'Ejercicio guardado correctamente.\n{archivo}')

    def _abrir_ejercicio(self):
        archivo = filedialog.askopenfilename(
            filetypes=[('Ejercicio de transporte', '*.json'), ('Todos', '*.*')],
            title='Abrir ejercicio guardado'
        )
        if not archivo:
            return

        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                d = json.load(f)
        except Exception as e:
            messagebox.showerror('Error al abrir', f'No se pudo leer el archivo:\n{e}')
            return

        try:
            if d.get('raw'):
                # Formato incompleto
                origenes = d.get('origenes', [])
                destinos = d.get('destinos', [])
                costos = d.get('costos', [])
                ofertas = d.get('ofertas', [])
                demandas = d.get('demandas', [])
            else:
                problema, nombre = dict_a_problema(d)
                origenes = problema.origenes
                destinos = problema.destinos
                costos = [[str(c) for c in fila] for fila in problema.costos]
                ofertas = [str(o) for o in problema.ofertas]
                demandas = [str(dem) for dem in problema.demandas]
                self._nombre_ejercicio.set(nombre)

            m = len(origenes)
            n = len(destinos)
            self._num_origenes.set(m)
            self._num_destinos.set(n)
            self._crear_tabla(inicial=True)
            self._tabla_costos_widget.cargar_datos(
                costos, ofertas, demandas,
                origenes=origenes, destinos=destinos
            )
            self._set_estado(f'Ejercicio abierto: {os.path.basename(archivo)}')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo cargar el ejercicio:\n{e}')

    def _exportar_resultados(self):
        if not self._resultado_costo:
            messagebox.showwarning('Aviso',
                                    'Primero resuelva un ejercicio para poder exportar resultados.')
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[
                ('Archivo de texto', '*.txt'),
                ('Archivo CSV', '*.csv'),
                ('Todos', '*.*')
            ],
            title='Exportar resultados',
            initialfile='resultados_esquina_noroeste'
        )
        if not archivo:
            return

        es_csv = archivo.lower().endswith('.csv')

        try:
            if es_csv:
                self._exportar_csv(archivo)
            else:
                self._exportar_txt(archivo)
            self._set_estado(f'Resultados exportados: {os.path.basename(archivo)}')
            messagebox.showinfo('Exportación exitosa',
                                f'Los resultados fueron guardados en:\n{archivo}')
        except Exception as e:
            messagebox.showerror('Error al exportar', str(e))

    def _exportar_txt(self, archivo):
        """Exporta resultados completos a un archivo TXT."""
        p_orig = self._problema_original
        p_bal = self._problema_balanceado
        rc = self._resultado_costo
        nombre = self._nombre_ejercicio.get() or 'Sin nombre'

        with open(archivo, 'w', encoding='utf-8') as f:
            f.write('=' * 65 + '\n')
            f.write('  MÉTODO DE LA ESQUINA NOROESTE\n')
            f.write('  Investigación de Operaciones — Problemas de Transporte\n')
            f.write('=' * 65 + '\n\n')
            f.write(f'Ejercicio: {nombre}\n\n')

            f.write('PROBLEMA ORIGINAL\n')
            f.write('-' * 40 + '\n')
            f.write(f'Orígenes: {", ".join(p_orig.origenes)}\n')
            f.write(f'Destinos: {", ".join(p_orig.destinos)}\n')
            f.write(f'Oferta total: {_fmt(p_orig.oferta_total())}\n')
            f.write(f'Demanda total: {_fmt(p_orig.demanda_total())}\n')
            f.write(f'Diferencia: {_fmt(p_orig.diferencia())}\n')
            f.write(f'Estado: {"Balanceado" if p_orig.esta_balanceado() else "No balanceado"}\n\n')

            if self._tipo_ajuste != 'ninguno':
                f.write('AJUSTE DE BALANCE\n')
                f.write('-' * 40 + '\n')
                if self._tipo_ajuste == 'destino_ficticio':
                    f.write(f'Se agregó Destino Ficticio con demanda = {_fmt(self._ajuste_valor)}\n\n')
                else:
                    f.write(f'Se agregó Origen Ficticio con oferta = {_fmt(self._ajuste_valor)}\n\n')

            f.write('PROCEDIMIENTO PASO A PASO\n')
            f.write('-' * 40 + '\n')
            for paso in self._pasos:
                f.write(paso.descripcion() + '\n\n')

            f.write('TABLA DE ASIGNACIONES FINALES\n')
            f.write('-' * 40 + '\n')
            for linea in rc.desglose_lineas():
                f.write(linea + '\n')

            f.write('\nCÁLCULO DEL COSTO TOTAL\n')
            f.write('-' * 40 + '\n')
            f.write(rc.formula_desarrollada() + '\n\n')

            f.write('NOTA: Este resultado es una solución básica factible INICIAL.\n')
            f.write('El método de la esquina noroeste NO garantiza el costo mínimo.\n')
            if self._es_degenerado:
                f.write('\n⚠ DEGENERACIÓN: Número de asignaciones menor que m+n-1.\n')

    def _exportar_csv(self, archivo):
        """Exporta la tabla de asignaciones a CSV."""
        p_bal = self._problema_balanceado
        rc = self._resultado_costo
        m = p_bal.num_origenes()
        n = p_bal.num_destinos()

        with open(archivo, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Encabezado
            writer.writerow([''] + p_bal.destinos + ['Oferta'])
            for i in range(m):
                fila = [p_bal.origenes[i]]
                for j in range(n):
                    fila.append(formatear_numero(self._asignaciones[i][j]))
                fila.append(formatear_numero(p_bal.ofertas[i]))
                writer.writerow(fila)
            writer.writerow(['Demanda'] + [formatear_numero(d) for d in p_bal.demandas] + [''])

            writer.writerow([])
            writer.writerow(['COSTO TOTAL', formatear_numero(rc.costo_total)])
            writer.writerow([])
            writer.writerow(['DESGLOSE'])
            writer.writerow(['Origen', 'Destino', 'Cantidad', 'Costo unitario', 'Subtotal'])
            for t in rc.terminos:
                writer.writerow([t[0], t[1], formatear_numero(t[2]),
                                  formatear_numero(t[3]), formatear_numero(t[4])])

    # =========================================================================
    # Ayuda
    # =========================================================================

    def _mostrar_ayuda(self):
        VentanaAyuda(self)


# =============================================================================
# Punto de entrada
# =============================================================================

if __name__ == '__main__':
    app = AplicacionTransporte()
    app.mainloop()

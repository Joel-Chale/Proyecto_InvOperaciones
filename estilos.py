# =============================================================================
# estilos.py — Paleta de colores, fuentes y estilos para ttk
# Investigación de Operaciones — Método de la Esquina Noroeste
# =============================================================================

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------
COLOR = {
    # Fondo principal de la aplicación
    'fondo':              '#F0F4F8',
    # Panel lateral / encabezados de sección
    'panel':              '#FFFFFF',
    # Acento principal (azul petróleo)
    'primario':           '#1B6CA8',
    'primario_oscuro':    '#144E7B',
    'primario_claro':     '#D6E8F7',
    # Acento secundario (verde para éxito/confirmación)
    'exito':              '#28A745',
    'exito_claro':        '#D4EDDA',
    # Alerta / advertencia (naranja)
    'advertencia':        '#FD7E14',
    'advertencia_claro':  '#FFF3CD',
    # Error / peligro (rojo)
    'peligro':            '#DC3545',
    'peligro_claro':      '#F8D7DA',
    # Neutros
    'texto':              '#212529',
    'texto_secundario':   '#6C757D',
    'borde':              '#CED4DA',
    'borde_claro':        '#E9ECEF',
    # Celdas de la tabla
    'celda_normal':       '#FFFFFF',
    'celda_activa':       '#FFF3CD',   # Amarillo suave — celda en proceso
    'celda_asignada':     '#D4EDDA',   # Verde suave — celda asignada
    'celda_agotada':      '#E9ECEF',   # Gris claro — fila/columna agotada
    'celda_ficticia':     '#E8D5F7',   # Morado suave — elemento ficticio
    'celda_encabezado':   '#1B6CA8',   # Azul — encabezados de tabla
    'texto_encabezado':   '#FFFFFF',
    # Resultado final
    'resultado_fondo':    '#EBF5FB',
}

# ---------------------------------------------------------------------------
# Fuentes
# ---------------------------------------------------------------------------
FUENTE = {
    'titulo':     ('Segoe UI', 16, 'bold'),
    'subtitulo':  ('Segoe UI', 12, 'bold'),
    'seccion':    ('Segoe UI', 11, 'bold'),
    'normal':     ('Segoe UI', 10),
    'pequena':    ('Segoe UI', 9),
    'mono':       ('Consolas', 10),
    'mono_grande':('Consolas', 11),
    'boton':      ('Segoe UI', 10, 'bold'),
    'celda':      ('Segoe UI', 10),
    'celda_num':  ('Consolas', 10),
}

# ---------------------------------------------------------------------------
# Configurar estilos ttk
# ---------------------------------------------------------------------------

def configurar_estilos(root):
    """Aplica los estilos personalizados a todos los widgets ttk."""
    estilo = ttk.Style(root)
    estilo.theme_use('clam')  # Base limpia compatible con Windows/macOS/Linux

    # Fondo general
    root.configure(bg=COLOR['fondo'])

    # ── Frame ──────────────────────────────────────────────────────────────
    estilo.configure('TFrame', background=COLOR['fondo'])
    estilo.configure('Panel.TFrame', background=COLOR['panel'],
                     relief='flat')
    estilo.configure('Seccion.TFrame', background=COLOR['panel'],
                     relief='groove', borderwidth=1)

    # ── Label ──────────────────────────────────────────────────────────────
    estilo.configure('TLabel',
                     background=COLOR['fondo'],
                     foreground=COLOR['texto'],
                     font=FUENTE['normal'])

    estilo.configure('Titulo.TLabel',
                     font=FUENTE['titulo'],
                     foreground=COLOR['primario'],
                     background=COLOR['fondo'])

    estilo.configure('Subtitulo.TLabel',
                     font=FUENTE['subtitulo'],
                     foreground=COLOR['primario'],
                     background=COLOR['panel'])

    estilo.configure('Seccion.TLabel',
                     font=FUENTE['seccion'],
                     foreground=COLOR['texto'],
                     background=COLOR['panel'])

    estilo.configure('Pequena.TLabel',
                     font=FUENTE['pequena'],
                     foreground=COLOR['texto_secundario'],
                     background=COLOR['panel'])

    estilo.configure('Exito.TLabel',
                     font=FUENTE['normal'],
                     foreground=COLOR['exito'],
                     background=COLOR['panel'])

    estilo.configure('Peligro.TLabel',
                     font=FUENTE['normal'],
                     foreground=COLOR['peligro'],
                     background=COLOR['panel'])

    estilo.configure('Advertencia.TLabel',
                     font=FUENTE['normal'],
                     foreground=COLOR['advertencia'],
                     background=COLOR['panel'])

    estilo.configure('EncabezadoTabla.TLabel',
                     font=FUENTE['celda'],
                     foreground=COLOR['texto_encabezado'],
                     background=COLOR['celda_encabezado'],
                     anchor='center')

    # ── Button ─────────────────────────────────────────────────────────────
    estilo.configure('TButton',
                     font=FUENTE['boton'],
                     padding=(10, 6))

    # Botón primario (azul)
    estilo.configure('Primario.TButton',
                     font=FUENTE['boton'],
                     foreground='white',
                     background=COLOR['primario'],
                     padding=(12, 7),
                     relief='flat')
    estilo.map('Primario.TButton',
               background=[('active', COLOR['primario_oscuro']),
                            ('pressed', COLOR['primario_oscuro'])],
               foreground=[('active', 'white')])

    # Botón de éxito (verde)
    estilo.configure('Exito.TButton',
                     font=FUENTE['boton'],
                     foreground='white',
                     background=COLOR['exito'],
                     padding=(12, 7),
                     relief='flat')
    estilo.map('Exito.TButton',
               background=[('active', '#1E7E34'), ('pressed', '#1E7E34')],
               foreground=[('active', 'white')])

    # Botón de advertencia (naranja)
    estilo.configure('Advertencia.TButton',
                     font=FUENTE['boton'],
                     foreground='white',
                     background=COLOR['advertencia'],
                     padding=(12, 7),
                     relief='flat')
    estilo.map('Advertencia.TButton',
               background=[('active', '#E96B00'), ('pressed', '#E96B00')],
               foreground=[('active', 'white')])

    # Botón de peligro (rojo)
    estilo.configure('Peligro.TButton',
                     font=FUENTE['boton'],
                     foreground='white',
                     background=COLOR['peligro'],
                     padding=(12, 7),
                     relief='flat')
    estilo.map('Peligro.TButton',
               background=[('active', '#BD2130'), ('pressed', '#BD2130')],
               foreground=[('active', 'white')])

    # Botón pequeño/secundario
    estilo.configure('Secundario.TButton',
                     font=FUENTE['pequena'],
                     foreground=COLOR['primario'],
                     background=COLOR['primario_claro'],
                     padding=(8, 5),
                     relief='flat')
    estilo.map('Secundario.TButton',
               background=[('active', COLOR['borde']), ('pressed', COLOR['borde'])],
               foreground=[('active', COLOR['primario'])])

    # ── Entry ──────────────────────────────────────────────────────────────
    estilo.configure('TEntry',
                     font=FUENTE['celda_num'],
                     padding=4)

    # ── Notebook (pestañas) ────────────────────────────────────────────────
    estilo.configure('TNotebook',
                     background=COLOR['fondo'],
                     tabmargins=[2, 5, 2, 0])
    estilo.configure('TNotebook.Tab',
                     font=FUENTE['normal'],
                     padding=[14, 7],
                     background=COLOR['borde_claro'],
                     foreground=COLOR['texto'])
    estilo.map('TNotebook.Tab',
               background=[('selected', COLOR['primario']),
                            ('active', COLOR['primario_claro'])],
               foreground=[('selected', 'white'), ('active', COLOR['primario'])])

    # ── Scrollbar ──────────────────────────────────────────────────────────
    estilo.configure('TScrollbar',
                     background=COLOR['borde'],
                     troughcolor=COLOR['fondo'],
                     relief='flat')

    # ── LabelFrame ─────────────────────────────────────────────────────────
    estilo.configure('TLabelframe',
                     background=COLOR['panel'],
                     foreground=COLOR['primario'],
                     relief='groove',
                     borderwidth=1)
    estilo.configure('TLabelframe.Label',
                     font=FUENTE['seccion'],
                     foreground=COLOR['primario'],
                     background=COLOR['panel'])

    # ── Spinbox ────────────────────────────────────────────────────────────
    estilo.configure('TSpinbox',
                     font=FUENTE['normal'],
                     padding=4)

    # ── Separator ──────────────────────────────────────────────────────────
    estilo.configure('TSeparator',
                     background=COLOR['borde'])

    return estilo


# ---------------------------------------------------------------------------
# Utilidades de widget
# ---------------------------------------------------------------------------

def crear_scrollframe(padre, bg=None):
    """
    Crea un Frame con scrollbars vertical y horizontal embebidas en un Canvas.
    Retorna (frame_exterior, frame_interior).
    El contenido debe empaquetarse en frame_interior.
    """
    bg = bg or COLOR['panel']
    frame_ext = tk.Frame(padre, bg=bg)
    canvas = tk.Canvas(frame_ext, bg=bg, highlightthickness=0)
    scroll_v = ttk.Scrollbar(frame_ext, orient='vertical', command=canvas.yview)
    scroll_h = ttk.Scrollbar(frame_ext, orient='horizontal', command=canvas.xview)
    frame_int = tk.Frame(canvas, bg=bg)

    frame_int.bind(
        '<Configure>',
        lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )

    canvas.create_window((0, 0), window=frame_int, anchor='nw')
    canvas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)

    scroll_v.pack(side='right', fill='y')
    scroll_h.pack(side='bottom', fill='x')
    canvas.pack(side='left', fill='both', expand=True)

    # Scroll inteligente con la rueda del ratón al pasar el cursor sobre el contenedor
    def _on_mousewheel(event):
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        except Exception:
            pass

    def _bind_mouse(event):
        canvas.bind_all('<MouseWheel>', _on_mousewheel)

    def _unbind_mouse(event):
        canvas.unbind_all('<MouseWheel>')

    frame_ext.bind('<Enter>', _bind_mouse)
    frame_ext.bind('<Leave>', _unbind_mouse)
    canvas.bind('<Enter>', _bind_mouse)
    canvas.bind('<Leave>', _unbind_mouse)

    return frame_ext, frame_int


def separador(padre, pady=8):
    """Crea un separador horizontal con margen."""
    ttk.Separator(padre, orient='horizontal').pack(fill='x', pady=pady)


def etiqueta_seccion(padre, texto, bg=None):
    """Crea una etiqueta de sección con estilo consistente."""
    bg = bg or COLOR['panel']
    lbl = tk.Label(
        padre, text=f'  {texto}  ',
        font=FUENTE['seccion'],
        fg=COLOR['texto_encabezado'],
        bg=COLOR['primario'],
        anchor='w',
        padx=8, pady=4
    )
    lbl.pack(fill='x', pady=(8, 4))
    return lbl


def tooltip(widget, texto):
    """Añade un tooltip sencillo a cualquier widget."""
    tip_ventana = [None]

    def mostrar(event):
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 4
        tip = tk.Toplevel(widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f'+{x}+{y}')
        tk.Label(
            tip, text=texto,
            font=FUENTE['pequena'],
            bg='#FFFDE7', fg=COLOR['texto'],
            relief='solid', borderwidth=1,
            padx=6, pady=3
        ).pack()
        tip_ventana[0] = tip

    def ocultar(event):
        if tip_ventana[0]:
            tip_ventana[0].destroy()
            tip_ventana[0] = None

    widget.bind('<Enter>', mostrar)
    widget.bind('<Leave>', ocultar)

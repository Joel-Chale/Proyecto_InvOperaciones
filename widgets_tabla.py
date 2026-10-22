# =============================================================================
# widgets_tabla.py — Widgets reutilizables para la tabla de transporte
# Investigación de Operaciones — Método de la Esquina Noroeste
# =============================================================================

import tkinter as tk
from tkinter import ttk
from estilos import COLOR, FUENTE


# ---------------------------------------------------------------------------
# TablaCostos: tabla editable de costos, ofertas y demandas
# ---------------------------------------------------------------------------

class TablaCostos(tk.Frame):
    """
    Widget que muestra y permite editar la tabla de costos de transporte.
    Incluye columna de ofertas y fila de demandas.
    Actualiza automáticamente los totales al editar.
    """

    TAM_CELDA_W = 80   # Ancho mínimo de cada celda de costo
    TAM_CELDA_H = 32   # Alto de cada fila
    TAM_ETIQ_W  = 100  # Ancho de la columna de nombres

    def __init__(self, padre, origenes, destinos,
                 callback_cambio=None, solo_lectura=False, **kwargs):
        """
        origenes: lista de str con nombres de los orígenes
        destinos: lista de str con nombres de los destinos
        callback_cambio: función llamada cuando cambia algún valor
        solo_lectura: si True, los campos no son editables
        """
        super().__init__(padre, bg=COLOR['panel'], **kwargs)
        self.origenes = origenes
        self.destinos = destinos
        self.callback_cambio = callback_cambio
        self.solo_lectura = solo_lectura

        # Variables de Tkinter para cada celda
        self._vars_costos = {}      # (i,j) → StringVar
        self._vars_ofertas = {}     # i → StringVar
        self._vars_demandas = {}    # j → StringVar
        self._vars_nom_orig = {}    # i → StringVar (nombre editable)
        self._vars_nom_dest = {}    # j → StringVar (nombre editable)

        self._lbl_total_oferta = None
        self._lbl_total_demanda = None
        self._lbl_diferencia = None
        self._lbl_estado = None
        self._lbl_celda_total = None

        self._construir()

    # ── Construcción ──────────────────────────────────────────────────────

    def _construir(self):
        """Dibuja todos los elementos de la tabla."""
        # Limpiar widgets existentes
        for widget in self.winfo_children():
            widget.destroy()

        m = len(self.origenes)
        n = len(self.destinos)

        # ── Fila 0: encabezados de columnas (destinos) ──────────────────
        # Celda vacía esquina superior-izquierda
        tk.Label(
            self, text='Origen \\ Destino',
            font=FUENTE['pequena'], fg=COLOR['texto_encabezado'],
            bg=COLOR['celda_encabezado'], width=14,
            relief='flat', anchor='center'
        ).grid(row=0, column=0, rowspan=2, sticky='nsew', padx=1, pady=1)

        for j, dest in enumerate(self.destinos):
            var = tk.StringVar(value=dest)
            self._vars_nom_dest[j] = var
            if self.solo_lectura:
                lbl = tk.Label(
                    self, textvariable=var,
                    font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
                    bg=COLOR['celda_encabezado'],
                    relief='flat', anchor='center', width=10
                )
                lbl.grid(row=0, column=j + 1, sticky='nsew', padx=1, pady=1)
            else:
                entry = tk.Entry(
                    self, textvariable=var,
                    font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
                    bg=COLOR['celda_encabezado'],
                    relief='flat', justify='center', width=10,
                    insertbackground='white'
                )
                entry.grid(row=0, column=j + 1, sticky='nsew', padx=1, pady=1)
                var.trace_add('write', lambda *a, jj=j: self._nombre_dest_cambiado(jj))

        # Encabezado columna "Oferta"
        tk.Label(
            self, text='Oferta',
            font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario_oscuro'],
            relief='flat', anchor='center', width=9
        ).grid(row=0, column=n + 1, sticky='nsew', padx=1, pady=1)

        # ── Filas de datos (orígenes) ────────────────────────────────────
        for i, orig in enumerate(self.origenes):
            fila_grid = i + 2  # +2 por las 2 filas de encabezado

            # Nombre del origen (editable o etiqueta)
            var_nom = tk.StringVar(value=orig)
            self._vars_nom_orig[i] = var_nom
            if self.solo_lectura:
                tk.Label(
                    self, textvariable=var_nom,
                    font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
                    bg=COLOR['celda_encabezado'],
                    relief='flat', anchor='w', padx=4, width=14
                ).grid(row=fila_grid, column=0, sticky='nsew', padx=1, pady=1)
            else:
                entry_nom = tk.Entry(
                    self, textvariable=var_nom,
                    font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
                    bg=COLOR['celda_encabezado'],
                    relief='flat', justify='left', width=14,
                    insertbackground='white'
                )
                entry_nom.grid(row=fila_grid, column=0, sticky='nsew', padx=1, pady=1)
                var_nom.trace_add('write', lambda *a, ii=i: self._nombre_orig_cambiado(ii))

            # Celdas de costos
            for j in range(n):
                var_c = tk.StringVar(value='')
                self._vars_costos[(i, j)] = var_c
                if self.solo_lectura:
                    lbl = tk.Label(
                        self, textvariable=var_c,
                        font=FUENTE['celda_num'],
                        fg=COLOR['texto'], bg=COLOR['celda_normal'],
                        relief='groove', anchor='center', width=8
                    )
                    lbl.grid(row=fila_grid, column=j + 1, sticky='nsew', padx=1, pady=1)
                else:
                    entry_c = tk.Entry(
                        self, textvariable=var_c,
                        font=FUENTE['celda_num'],
                        fg=COLOR['texto'], bg=COLOR['celda_normal'],
                        relief='groove', justify='center', width=8
                    )
                    entry_c.grid(row=fila_grid, column=j + 1, sticky='nsew', padx=1, pady=1)
                    # Navegación con Tab/Enter
                    entry_c.bind('<Return>', lambda e, ii=i, jj=j: self._navegar(ii, jj, 0, 1))
                    entry_c.bind('<Tab>',    lambda e, ii=i, jj=j: self._navegar(ii, jj, 0, 1))
                    var_c.trace_add('write', self._on_valor_cambiado)

            # Campo de oferta
            var_of = tk.StringVar(value='')
            self._vars_ofertas[i] = var_of
            if self.solo_lectura:
                tk.Label(
                    self, textvariable=var_of,
                    font=FUENTE['celda_num'],
                    fg='white', bg=COLOR['primario_oscuro'],
                    relief='flat', anchor='center', width=9
                ).grid(row=fila_grid, column=n + 1, sticky='nsew', padx=1, pady=1)
            else:
                entry_of = tk.Entry(
                    self, textvariable=var_of,
                    font=FUENTE['celda_num'],
                    fg='white', bg=COLOR['primario_oscuro'],
                    relief='flat', justify='center', width=9,
                    insertbackground='white'
                )
                entry_of.grid(row=fila_grid, column=n + 1, sticky='nsew', padx=1, pady=1)
                var_of.trace_add('write', self._on_valor_cambiado)

        # ── Fila de demandas ─────────────────────────────────────────────
        fila_dem = m + 2
        tk.Label(
            self, text='Demanda',
            font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario_oscuro'],
            relief='flat', anchor='center', width=14
        ).grid(row=fila_dem, column=0, sticky='nsew', padx=1, pady=1)

        for j in range(n):
            var_d = tk.StringVar(value='')
            self._vars_demandas[j] = var_d
            if self.solo_lectura:
                tk.Label(
                    self, textvariable=var_d,
                    font=FUENTE['celda_num'],
                    fg='white', bg=COLOR['primario_oscuro'],
                    relief='flat', anchor='center', width=8
                ).grid(row=fila_dem, column=j + 1, sticky='nsew', padx=1, pady=1)
            else:
                entry_d = tk.Entry(
                    self, textvariable=var_d,
                    font=FUENTE['celda_num'],
                    fg='white', bg=COLOR['primario_oscuro'],
                    relief='flat', justify='center', width=8,
                    insertbackground='white'
                )
                entry_d.grid(row=fila_dem, column=j + 1, sticky='nsew', padx=1, pady=1)
                var_d.trace_add('write', self._on_valor_cambiado)

        # Celda esquina inferior derecha (Demanda \ Oferta)
        self._lbl_celda_total = tk.Label(
            self, text='',
            font=FUENTE['pequena'], fg='white',
            bg=COLOR['primario_oscuro'],
            relief='flat', anchor='center', width=11
        )
        self._lbl_celda_total.grid(row=fila_dem, column=n + 1, sticky='nsew', padx=1, pady=1)

        # ── Fila de resumen (totales, diferencia, estado) ────────────────
        fila_res = m + 3
        tk.Label(
            self, text='Total oferta:',
            font=FUENTE['pequena'], fg=COLOR['texto_secundario'],
            bg=COLOR['panel'], anchor='e'
        ).grid(row=fila_res, column=0, sticky='e', padx=4, pady=2)

        self._lbl_total_oferta = tk.Label(
            self, text='—',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], anchor='w'
        )
        self._lbl_total_oferta.grid(row=fila_res, column=1, columnspan=2,
                                     sticky='w', pady=2)

        tk.Label(
            self, text='Total demanda:',
            font=FUENTE['pequena'], fg=COLOR['texto_secundario'],
            bg=COLOR['panel'], anchor='e'
        ).grid(row=fila_res, column=3, sticky='e', padx=4)

        self._lbl_total_demanda = tk.Label(
            self, text='—',
            font=FUENTE['seccion'], fg=COLOR['primario'],
            bg=COLOR['panel'], anchor='w'
        )
        self._lbl_total_demanda.grid(row=fila_res, column=4, columnspan=2,
                                      sticky='w')

        fila_res2 = m + 4
        tk.Label(
            self, text='Diferencia:',
            font=FUENTE['pequena'], fg=COLOR['texto_secundario'],
            bg=COLOR['panel'], anchor='e'
        ).grid(row=fila_res2, column=0, sticky='e', padx=4, pady=2)

        self._lbl_diferencia = tk.Label(
            self, text='—',
            font=FUENTE['seccion'], bg=COLOR['panel'], anchor='w'
        )
        self._lbl_diferencia.grid(row=fila_res2, column=1, columnspan=2,
                                   sticky='w')

        fila_res3 = m + 5
        self._lbl_estado = tk.Label(
            self, text='',
            font=FUENTE['normal'], bg=COLOR['panel'], anchor='w',
            wraplength=600
        )
        self._lbl_estado.grid(row=fila_res3, column=0,
                               columnspan=n + 2, sticky='w', padx=4, pady=4)

        # Configurar pesos de columnas para expandir
        for col in range(n + 2):
            self.columnconfigure(col, weight=1)

    # ── Eventos ───────────────────────────────────────────────────────────

    def _on_valor_cambiado(self, *args):
        """Actualiza los totales cada vez que cambia un valor."""
        self._actualizar_totales()
        if self.callback_cambio:
            self.callback_cambio()

    def _nombre_orig_cambiado(self, i):
        nuevo = self._vars_nom_orig[i].get()
        if i < len(self.origenes):
            self.origenes[i] = nuevo

    def _nombre_dest_cambiado(self, j):
        nuevo = self._vars_nom_dest[j].get()
        if j < len(self.destinos):
            self.destinos[j] = nuevo

    def _navegar(self, fila, col, df, dc):
        """Mueve el foco al siguiente campo en la dirección indicada."""
        n = len(self.destinos)
        nueva_col = col + dc
        nueva_fila = fila + df
        if nueva_col >= n:
            nueva_col = 0
            nueva_fila += 1
        clave = (nueva_fila, nueva_col)
        if clave in self._vars_costos:
            # Buscar el Entry correspondiente y darle foco
            for widget in self.winfo_children():
                info = widget.grid_info()
                r = info.get('row', -1)
                c = info.get('column', -1)
                if r == nueva_fila + 2 and c == nueva_col + 1:
                    widget.focus_set()
                    break
        return 'break'

    def _actualizar_totales(self):
        """Recalcula y muestra oferta total, demanda total, diferencia y estado."""
        try:
            from decimal import Decimal
            from logica import formatear_numero
            total_of = Decimal('0')
            for var in self._vars_ofertas.values():
                v = var.get().strip()
                if v:
                    total_of += Decimal(v)

            total_dem = Decimal('0')
            for var in self._vars_demandas.values():
                v = var.get().strip()
                if v:
                    total_dem += Decimal(v)

            str_of = formatear_numero(total_of)
            str_dem = formatear_numero(total_dem)
            dif = total_of - total_dem
            str_dif = formatear_numero(dif)

            self._lbl_total_oferta.config(text=str_of)
            self._lbl_total_demanda.config(text=str_dem)
            self._lbl_diferencia.config(text=str_dif)
            if self._lbl_celda_total:
                self._lbl_celda_total.config(text=f"{str_dem} \\ {str_of}")

            if total_of == Decimal('0') and total_dem == Decimal('0'):
                self._lbl_estado.config(text='', fg=COLOR['texto'])
            elif dif == Decimal('0'):
                self._lbl_estado.config(
                    text='✔ El problema está balanceado. Se puede aplicar directamente '
                         'el Método de la Esquina Noroeste.',
                    fg=COLOR['exito']
                )
            elif dif > Decimal('0'):
                self._lbl_estado.config(
                    text=f'⚠ El problema NO está balanceado. La oferta supera a la demanda '
                         f'en {formatear_numero(dif)} unidades. Se agregará automáticamente un Destino Ficticio.',
                    fg=COLOR['advertencia']
                )
            else:
                self._lbl_estado.config(
                    text=f'⚠ El problema NO está balanceado. La demanda supera a la oferta '
                         f'en {formatear_numero(abs(dif))} unidades. Se agregará automáticamente un Origen Ficticio.',
                    fg=COLOR['advertencia']
                )
        except Exception:
            pass  # Mientras el usuario escribe datos incompletos, no mostrar error

    # ── API pública ───────────────────────────────────────────────────────

    def obtener_datos(self):
        """
        Retorna (costos_txt, ofertas_txt, demandas_txt, nombres_orig, nombres_dest).
        Todos los valores son strings tal como los escribió el usuario.
        """
        m = len(self.origenes)
        n = len(self.destinos)
        costos_txt = [[self._vars_costos[(i, j)].get() for j in range(n)] for i in range(m)]
        ofertas_txt = [self._vars_ofertas[i].get() for i in range(m)]
        demandas_txt = [self._vars_demandas[j].get() for j in range(n)]
        nombres_orig = [self._vars_nom_orig[i].get() for i in range(m)]
        nombres_dest = [self._vars_nom_dest[j].get() for j in range(n)]
        return costos_txt, ofertas_txt, demandas_txt, nombres_orig, nombres_dest

    def cargar_datos(self, costos, ofertas, demandas, origenes=None, destinos=None):
        """Carga datos en la tabla. Todos los valores deben ser strings."""
        m = len(self.origenes)
        n = len(self.destinos)

        if origenes:
            for i in range(min(m, len(origenes))):
                self._vars_nom_orig[i].set(origenes[i])
        if destinos:
            for j in range(min(n, len(destinos))):
                self._vars_nom_dest[j].set(destinos[j])

        for i in range(min(m, len(costos))):
            for j in range(min(n, len(costos[i]))):
                if (i, j) in self._vars_costos:
                    self._vars_costos[(i, j)].set(str(costos[i][j]))

        for i in range(min(m, len(ofertas))):
            if i in self._vars_ofertas:
                self._vars_ofertas[i].set(str(ofertas[i]))

        for j in range(min(n, len(demandas))):
            if j in self._vars_demandas:
                self._vars_demandas[j].set(str(demandas[j]))

        self._actualizar_totales()

    def limpiar(self):
        """Pone en blanco todos los campos de costos, ofertas y demandas."""
        for var in self._vars_costos.values():
            var.set('')
        for var in self._vars_ofertas.values():
            var.set('')
        for var in self._vars_demandas.values():
            var.set('')
        self._actualizar_totales()

    def resaltar_celda(self, fila, col, color_fondo):
        """Cambia el color de fondo de una celda de costo específica."""
        for widget in self.winfo_children():
            info = widget.grid_info()
            r = info.get('row', -1)
            c = info.get('column', -1)
            if r == fila + 2 and c == col + 1:
                widget.config(bg=color_fondo)
                break

    def restaurar_colores(self):
        """Restaura todos los colores de las celdas de costo al valor original."""
        n = len(self.destinos)
        m = len(self.origenes)
        for widget in self.winfo_children():
            info = widget.grid_info()
            r = info.get('row', -1)
            c = info.get('column', -1)
            # Solo celdas de costo (filas 2..m+1, columnas 1..n)
            if 2 <= r <= m + 1 and 1 <= c <= n:
                try:
                    widget.config(bg=COLOR['celda_normal'])
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# TablaAsignaciones: tabla de solo lectura con asignaciones resaltadas
# ---------------------------------------------------------------------------

class TablaAsignaciones(tk.Frame):
    """
    Muestra la tabla de asignaciones del método de la esquina noroeste.
    Solo lectura. Resalta las celdas con asignaciones positivas.
    Soporta marcado de ficticias.
    """

    def __init__(self, padre, problema, asignaciones,
                 indices_ficticios=None, celda_activa=None,
                 asignaciones_acumuladas=None, **kwargs):
        """
        problema: ProblemaTransporte
        asignaciones: matriz [[Decimal]] con las cantidades asignadas
        indices_ficticios: dict con claves 'origen' (int o None) y 'destino' (int o None)
        celda_activa: (fila, col) de la celda que se está procesando actualmente
        asignaciones_acumuladas: si se pasa, solo muestra estas asignaciones (para paso a paso)
        """
        super().__init__(padre, bg=COLOR['panel'], **kwargs)
        self.problema = problema
        self.asignaciones = asignaciones
        self.indices_ficticios = indices_ficticios or {}
        self.celda_activa = celda_activa
        self.asignaciones_acum = asignaciones_acumuladas
        self._construir()

    def _construir(self):
        from decimal import Decimal
        from logica import formatear_numero

        p = self.problema
        m = p.num_origenes()
        n = p.num_destinos()
        datos = self.asignaciones_acum if self.asignaciones_acum else self.asignaciones
        fict_orig = self.indices_ficticios.get('origen')
        fict_dest = self.indices_ficticios.get('destino')

        # Fila 0: encabezados de destinos
        tk.Label(
            self, text='',
            bg=COLOR['celda_encabezado'], width=13, relief='flat'
        ).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)

        for j, dest in enumerate(p.destinos):
            es_fict = (j == fict_dest)
            bg = COLOR['celda_ficticia'] if es_fict else COLOR['celda_encabezado']
            fg = COLOR['texto'] if es_fict else COLOR['texto_encabezado']
            tk.Label(
                self, text=dest,
                font=FUENTE['celda'], fg=fg, bg=bg,
                width=10, relief='flat', anchor='center'
            ).grid(row=0, column=j + 1, sticky='nsew', padx=1, pady=1)

        tk.Label(
            self, text='Oferta',
            font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario_oscuro'],
            width=9, relief='flat', anchor='center'
        ).grid(row=0, column=n + 1, sticky='nsew', padx=1, pady=1)

        # Filas de datos
        for i, orig in enumerate(p.origenes):
            fila_grid = i + 1
            es_fict_orig = (i == fict_orig)
            bg_nom = COLOR['celda_ficticia'] if es_fict_orig else COLOR['celda_encabezado']
            fg_nom = COLOR['texto'] if es_fict_orig else COLOR['texto_encabezado']
            tk.Label(
                self, text=orig,
                font=FUENTE['celda'], fg=fg_nom, bg=bg_nom,
                width=13, relief='flat', anchor='w', padx=4
            ).grid(row=fila_grid, column=0, sticky='nsew', padx=1, pady=1)

            for j in range(n):
                cant = datos[i][j]
                es_activa = (self.celda_activa == (i, j))
                es_fict_celda = (i == fict_orig or j == fict_dest)

                if es_activa:
                    bg_celda = COLOR['celda_activa']
                    border_w = 2
                elif cant > Decimal('0'):
                    bg_celda = COLOR['celda_ficticia'] if es_fict_celda else COLOR['celda_asignada']
                    border_w = 1
                else:
                    bg_celda = COLOR['celda_agotada'] if es_fict_celda else COLOR['celda_normal']
                    border_w = 1

                                #Parte mostrar las asignaciones en la tabla
                costo_unit = formatear_numero(p.costos[i][j])
                cant_str = formatear_numero(cant) if cant > Decimal('0') else ''

                # Contenedor de la celda
                frame_c = tk.Frame(self, bg=bg_celda, relief='groove', borderwidth=border_w, width=65, height=44)
                frame_c.grid(row=fila_grid, column=j + 1, sticky='nsew', padx=1, pady=1)
                frame_c.grid_propagate(False)

                # Costo original ingresado (arriba a la derecha en pequeño)
                tk.Label(
                    frame_c, text=f'c: {costo_unit}',
                    font=('Segoe UI', 8), fg=COLOR['texto_secundario'],
                    bg=bg_celda, anchor='ne'
                ).pack(side='top', fill='x', padx=2, pady=1)

                # Cantidad asignada (en el centro en negrita)
                tk.Label(
                    frame_c, text=cant_str,
                    font=('Consolas', 11, 'bold' if cant > Decimal('0') else 'normal'),
                    fg=COLOR['primario_oscuro'] if cant > Decimal('0') else COLOR['texto_secundario'],
                    bg=bg_celda
                ).pack(expand=True)

            # Oferta en la fila
            tk.Label(
                self, text=formatear_numero(p.ofertas[i]),
                font=FUENTE['celda_num'],
                fg='white', bg=COLOR['primario_oscuro'],
                width=9, relief='flat', anchor='center'
            ).grid(row=fila_grid, column=n + 1, sticky='nsew', padx=1, pady=1)

        # Fila de demandas
        fila_dem = m + 1
        tk.Label(
            self, text='Demanda',
            font=FUENTE['celda'], fg=COLOR['texto_encabezado'],
            bg=COLOR['primario_oscuro'],
            width=13, relief='flat', anchor='center'
        ).grid(row=fila_dem, column=0, sticky='nsew', padx=1, pady=1)

        for j in range(n):
            es_fict = (j == fict_dest)
            tk.Label(
                self, text=formatear_numero(p.demandas[j]),
                font=FUENTE['celda_num'],
                fg='white',
                bg=COLOR['celda_ficticia'] if es_fict else COLOR['primario_oscuro'],
                width=8, relief='flat', anchor='center'
            ).grid(row=fila_dem, column=j + 1, sticky='nsew', padx=1, pady=1)

        # Esquina inferior derecha: Demanda \ Oferta
        tot_dem = formatear_numero(p.demanda_total())
        tot_of = formatear_numero(p.oferta_total())
        texto_totales = f"{tot_dem} \\ {tot_of}"

        tk.Label(
            self, text=texto_totales,
            font=FUENTE['pequena'], fg='white',
            bg=COLOR['primario_oscuro'], width=11, relief='flat', anchor='center'
        ).grid(row=fila_dem, column=n + 1, sticky='nsew', padx=1, pady=1)

        for col in range(n + 2):
            self.columnconfigure(col, weight=1)

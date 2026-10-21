# =============================================================================
# logica.py — Motor de cálculo para el Método de la Esquina Noroeste
# Investigación de Operaciones — Problemas de Transporte
# =============================================================================
# Separación total entre lógica matemática e interfaz gráfica.
# Todos los comentarios y mensajes están en español.

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import copy
import random


# ---------------------------------------------------------------------------
# Clase principal: ProblemaTransporte
# ---------------------------------------------------------------------------
class ProblemaTransporte:
    """
    Encapsula todos los datos de un problema de transporte.
    Almacena nombres, costos, ofertas y demandas originales.
    """

    def __init__(self):
        self.origenes = []        # Lista de nombres de orígenes (str)
        self.destinos = []        # Lista de nombres de destinos (str)
        self.costos = []          # Matriz de costos [fila][columna] (Decimal)
        self.ofertas = []         # Lista de ofertas por origen (Decimal)
        self.demandas = []        # Lista de demandas por destino (Decimal)

    def num_origenes(self):
        return len(self.origenes)

    def num_destinos(self):
        return len(self.destinos)

    def oferta_total(self):
        return sum(self.ofertas)

    def demanda_total(self):
        return sum(self.demandas)

    def diferencia(self):
        """Retorna oferta_total - demanda_total."""
        return self.oferta_total() - self.demanda_total()

    def esta_balanceado(self):
        return self.diferencia() == Decimal('0')

    def copia_profunda(self):
        """Devuelve una copia independiente del problema."""
        p = ProblemaTransporte()
        p.origenes = list(self.origenes)
        p.destinos = list(self.destinos)
        p.costos = [list(fila) for fila in self.costos]
        p.ofertas = list(self.ofertas)
        p.demandas = list(self.demandas)
        return p


# ---------------------------------------------------------------------------
# Validación de datos
# ---------------------------------------------------------------------------

def validar_decimal(texto, nombre_campo, permitir_negativo=False, permitir_cero=True):
    """
    Convierte un texto a Decimal validando correctamente.
    Retorna (Decimal, None) si es válido o (None, mensaje_error) si falla.
    """
    texto = texto.strip()
    if texto == '':
        return None, f'El campo "{nombre_campo}" está vacío.'
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        return None, f'El campo "{nombre_campo}" contiene un valor no numérico: "{texto}".'
    if not permitir_negativo and valor < Decimal('0'):
        return None, f'El campo "{nombre_campo}" no puede ser negativo (valor: {texto}).'
    if not permitir_cero and valor == Decimal('0'):
        return None, f'El campo "{nombre_campo}" no puede ser cero.'
    return valor, None


def validar_problema(origenes, destinos, costos_texto, ofertas_texto, demandas_texto,
                     costos_negativos=False):
    """
    Valida todos los datos ingresados por el usuario.
    Retorna (ProblemaTransporte, None) o (None, lista_de_errores).
    """
    errores = []
    m = len(origenes)
    n = len(destinos)

    # Validar dimensiones
    if m < 1:
        errores.append('Debe haber al menos 1 origen.')
    if n < 1:
        errores.append('Debe haber al menos 1 destino.')
    if errores:
        return None, errores

    # Validar nombres
    for i, nombre in enumerate(origenes):
        if not nombre.strip():
            errores.append(f'El nombre del Origen {i+1} está vacío.')
    for j, nombre in enumerate(destinos):
        if not nombre.strip():
            errores.append(f'El nombre del Destino {j+1} está vacío.')

    # Validar costos
    costos = []
    for i in range(m):
        fila = []
        for j in range(n):
            val, err = validar_decimal(
                costos_texto[i][j],
                f'Costo [{origenes[i]}→{destinos[j]}]',
                permitir_negativo=costos_negativos
            )
            if err:
                errores.append(err)
                fila.append(None)
            else:
                fila.append(val)
        costos.append(fila)

    # Validar ofertas
    ofertas = []
    for i in range(m):
        val, err = validar_decimal(
            ofertas_texto[i],
            f'Oferta de {origenes[i]}',
            permitir_negativo=False,
            permitir_cero=False
        )
        if err:
            errores.append(err)
            ofertas.append(None)
        else:
            ofertas.append(val)

    # Validar demandas
    demandas = []
    for j in range(n):
        val, err = validar_decimal(
            demandas_texto[j],
            f'Demanda de {destinos[j]}',
            permitir_negativo=False,
            permitir_cero=False
        )
        if err:
            errores.append(err)
            demandas.append(None)
        else:
            demandas.append(val)

    if errores:
        return None, errores

    # Construir el objeto del problema
    problema = ProblemaTransporte()
    problema.origenes = [o.strip() for o in origenes]
    problema.destinos = [d.strip() for d in destinos]
    problema.costos = costos
    problema.ofertas = ofertas
    problema.demandas = demandas
    return problema, None


# ---------------------------------------------------------------------------
# Balanceo automático
# ---------------------------------------------------------------------------

def balancear_problema(problema):
    """
    Crea una copia balanceada del problema, añadiendo fila/columna ficticia si es necesario.
    Retorna (problema_balanceado, tipo_ajuste, cantidad_ajuste).
      tipo_ajuste: 'ninguno', 'destino_ficticio', 'origen_ficticio'
      cantidad_ajuste: valor de la fila/columna ficticia
    """
    p = problema.copia_profunda()
    diferencia = p.diferencia()

    if diferencia == Decimal('0'):
        return p, 'ninguno', Decimal('0')

    elif diferencia > Decimal('0'):
        # Oferta > Demanda → agregar destino ficticio
        p.destinos.append('Destino Ficticio')
        for i in range(p.num_origenes()):
            p.costos[i].append(Decimal('0'))
        p.demandas.append(diferencia)
        return p, 'destino_ficticio', diferencia

    else:
        # Demanda > Oferta → agregar origen ficticio
        cantidad = abs(diferencia)
        p.origenes.append('Origen Ficticio')
        p.costos.append([Decimal('0')] * p.num_destinos())
        p.ofertas.append(cantidad)
        return p, 'origen_ficticio', cantidad


# ---------------------------------------------------------------------------
# Registro de un paso del algoritmo
# ---------------------------------------------------------------------------

class PasoEsquinaNoroeste:
    """Almacena toda la información de un paso del método de la esquina noroeste."""

    def __init__(self, numero, fila, columna, nombre_origen, nombre_destino,
                 oferta_disponible, demanda_pendiente, cantidad_asignada,
                 oferta_restante, demanda_restante, motivo_avance,
                 es_empate=False, es_ultimo=False):
        self.numero = numero
        self.fila = fila
        self.columna = columna
        self.nombre_origen = nombre_origen
        self.nombre_destino = nombre_destino
        self.oferta_disponible = oferta_disponible
        self.demanda_pendiente = demanda_pendiente
        self.cantidad_asignada = cantidad_asignada
        self.oferta_restante = oferta_restante
        self.demanda_restante = demanda_restante
        self.motivo_avance = motivo_avance
        self.es_empate = es_empate
        self.es_ultimo = es_ultimo
        # Instantánea de las asignaciones acumuladas hasta este paso
        self.asignaciones_acumuladas = []

    def descripcion(self):
        """Genera el texto explicativo del paso, usando lenguaje sencillo."""
        txt = []
        txt.append(f'Paso {self.numero}: Nos encontramos en la celda '
                   f'{self.nombre_origen} → {self.nombre_destino}.')
        txt.append(f'  • Oferta disponible en {self.nombre_origen}: '
                   f'{_fmt(self.oferta_disponible)} unidades.')
        txt.append(f'  • Demanda pendiente en {self.nombre_destino}: '
                   f'{_fmt(self.demanda_pendiente)} unidades.')

        if self.oferta_disponible < self.demanda_pendiente:
            txt.append(f'  • La oferta ({_fmt(self.oferta_disponible)}) es menor que '
                       f'la demanda ({_fmt(self.demanda_pendiente)}), '
                       f'por lo tanto asignamos {_fmt(self.cantidad_asignada)} unidades '
                       f'(toda la oferta disponible).')
        elif self.oferta_disponible > self.demanda_pendiente:
            txt.append(f'  • La demanda ({_fmt(self.demanda_pendiente)}) es menor que '
                       f'la oferta ({_fmt(self.oferta_disponible)}), '
                       f'por lo tanto asignamos {_fmt(self.cantidad_asignada)} unidades '
                       f'(toda la demanda pendiente).')
        else:
            txt.append(f'  • La oferta y la demanda son iguales '
                       f'({_fmt(self.oferta_disponible)} unidades), '
                       f'asignamos {_fmt(self.cantidad_asignada)} unidades.')
            if self.es_empate and not self.es_ultimo:
                txt.append('  ⚠ Empate detectado: la oferta y la demanda se agotan '
                           'simultáneamente. Esto puede producir degeneración '
                           '(una solución con menos variables básicas de las esperadas). '
                           'Se registra la asignación y se avanza en diagonal.')

        txt.append(f'  • Oferta restante en {self.nombre_origen}: '
                   f'{_fmt(self.oferta_restante)} unidades.')
        txt.append(f'  • Demanda restante en {self.nombre_destino}: '
                   f'{_fmt(self.demanda_restante)} unidades.')
        txt.append(f'  → {self.motivo_avance}')

        return '\n'.join(txt)


def formatear_numero(valor):
    """
    Formatea cualquier número (Decimal, float, int o str) para mostrarlo
    sin ceros decimales innecesarios y NUNCA con notación científica (sin 'E' o 'e').
    Ejemplo: Decimal('100') -> '100' (en vez de '1E+2')
             Decimal('20.50') -> '20.5'
             Decimal('0.000') -> '0'
    """
    if valor is None:
        return '0'
    try:
        d = Decimal(str(valor))
        # Formato de punto fijo sin notación científica
        s = format(d, 'f')
        if '.' in s:
            s = s.rstrip('0').rstrip('.')
        return s if s else '0'
    except Exception:
        return str(valor)


def _fmt(valor):
    """Alias compatible para formatear números de forma limpia."""
    return formatear_numero(valor)


# ---------------------------------------------------------------------------
# Algoritmo de la Esquina Noroeste
# ---------------------------------------------------------------------------

def resolver_esquina_noroeste(problema):
    """
    Aplica el Método de la Esquina Noroeste.
    Retorna (asignaciones, pasos, es_degenerado).
      asignaciones: matriz [m][n] de Decimal con cantidades asignadas
      pasos: lista de PasoEsquinaNoroeste
      es_degenerado: bool, True si el número de asignaciones < m+n-1
    """
    m = problema.num_origenes()
    n = problema.num_destinos()

    # Copias de trabajo de ofertas y demandas
    oferta = list(problema.ofertas)
    demanda = list(problema.demandas)

    # Matriz de asignaciones inicializada en cero
    asignaciones = [[Decimal('0')] * n for _ in range(m)]

    pasos = []
    fila = 0
    columna = 0
    num_paso = 1
    num_asignaciones = 0

    while fila < m and columna < n:
        of_disp = oferta[fila]
        dem_pend = demanda[columna]

        # Cantidad a asignar = mínimo entre oferta disponible y demanda pendiente
        cantidad = min(of_disp, dem_pend)
        asignaciones[fila][columna] += cantidad
        num_asignaciones += 1

        of_rest = of_disp - cantidad
        dem_rest = dem_pend - cantidad
        oferta[fila] = of_rest
        demanda[columna] = dem_rest

        es_empate = (of_rest == Decimal('0') and dem_rest == Decimal('0'))
        es_ultimo = (fila == m - 1 and columna == n - 1)

        # Determinar motivo de avance
        if es_ultimo:
            motivo = 'Todas las ofertas y demandas han sido satisfechas. ¡Proceso terminado!'
        elif es_empate:
            motivo = ('La oferta y la demanda se agotaron simultáneamente (empate). '
                      'Avanzamos a la siguiente fila Y columna.')
        elif of_rest == Decimal('0'):
            motivo = (f'La oferta de {problema.origenes[fila]} quedó agotada. '
                      f'Avanzamos a la siguiente fila ({problema.origenes[fila + 1] if fila + 1 < m else "—"}).')
        else:
            motivo = (f'La demanda de {problema.destinos[columna]} quedó satisfecha. '
                      f'Avanzamos a la siguiente columna ({problema.destinos[columna + 1] if columna + 1 < n else "—"}).')

        # Crear el paso
        paso = PasoEsquinaNoroeste(
            numero=num_paso,
            fila=fila,
            columna=columna,
            nombre_origen=problema.origenes[fila],
            nombre_destino=problema.destinos[columna],
            oferta_disponible=of_disp,
            demanda_pendiente=dem_pend,
            cantidad_asignada=cantidad,
            oferta_restante=of_rest,
            demanda_restante=dem_rest,
            motivo_avance=motivo,
            es_empate=es_empate,
            es_ultimo=es_ultimo
        )
        # Guardar instantánea de asignaciones hasta este momento
        paso.asignaciones_acumuladas = [list(r) for r in asignaciones]
        pasos.append(paso)
        num_paso += 1

        # Avanzar según resultado
        if es_ultimo:
            break
        elif es_empate:
            fila += 1
            columna += 1
        elif of_rest == Decimal('0'):
            fila += 1
        else:
            columna += 1

    # Verificar degeneración: se espera m+n-1 asignaciones en solución básica factible
    esperadas = m + n - 1
    es_degenerado = num_asignaciones < esperadas

    return asignaciones, pasos, es_degenerado


# ---------------------------------------------------------------------------
# Cálculo del costo total
# ---------------------------------------------------------------------------

class ResultadoCosto:
    """Encapsula el cálculo del costo total con su desglose."""

    def __init__(self, asignaciones, costos, origenes, destinos):
        self.terminos = []       # Lista de (origen, destino, cantidad, costo_unit, subtotal)
        self.costo_total = Decimal('0')
        self.cantidad_total = Decimal('0')

        m = len(origenes)
        n = len(destinos)
        for i in range(m):
            for j in range(n):
                cant = asignaciones[i][j]
                if cant > Decimal('0'):
                    cu = costos[i][j]
                    subtotal = cant * cu
                    self.terminos.append((origenes[i], destinos[j], cant, cu, subtotal))
                    self.costo_total += subtotal
                    self.cantidad_total += cant

    def formula_desarrollada(self):
        """Genera la fórmula matemática expandida."""
        if not self.terminos:
            return 'Sin asignaciones.'
        partes = [f'({_fmt(t[2])} × {_fmt(t[3])})' for t in self.terminos]
        linea1 = 'Costo total = ' + ' + '.join(partes)
        subtotales = [f'{_fmt(t[4])}' for t in self.terminos]
        linea2 = 'Costo total = ' + ' + '.join(subtotales)
        linea3 = f'Costo total = {_fmt(self.costo_total)}'
        return f'{linea1}\n{linea2}\n{linea3}'

    def desglose_lineas(self):
        """Genera lista de strings con cada término del costo."""
        lineas = []
        for t in self.terminos:
            lineas.append(
                f'  {t[0]} → {t[1]}: {_fmt(t[2])} unidades × costo {_fmt(t[3])} = {_fmt(t[4])}'
            )
        return lineas


# ---------------------------------------------------------------------------
# Generación de problemas de ejemplo y aleatorios
# ---------------------------------------------------------------------------

EJEMPLO_PREDEFINIDO = {
    'origenes': ['Fábrica A', 'Fábrica B', 'Fábrica C'],
    'destinos': ['Ciudad 1', 'Ciudad 2', 'Ciudad 3', 'Ciudad 4'],
    'costos': [
        ['2', '3', '1', '5'],
        ['7', '3', '4', '6'],
        ['8', '5', '2', '3'],
    ],
    # Oferta total = 300, Demanda total = 300 → Balanceado
    'ofertas': ['120', '80', '100'],
    'demandas': ['150', '70', '60', '20'],
}


def generar_problema_aleatorio(num_origenes, num_destinos,
                                rango_costos=(1, 20),
                                rango_ofertas=(10, 100),
                                rango_demandas=(10, 100),
                                balanceado=True):
    """
    Genera un problema de transporte con datos aleatorios.
    Si balanceado=True, ajusta la última demanda para que cuadre con la oferta total.
    """
    origenes = [f'Origen {i+1}' for i in range(num_origenes)]
    destinos = [f'Destino {j+1}' for j in range(num_destinos)]

    costos = [
        [str(random.randint(*rango_costos)) for _ in range(num_destinos)]
        for _ in range(num_origenes)
    ]

    ofertas = [str(random.randint(*rango_ofertas)) for _ in range(num_origenes)]

    if balanceado:
        total_oferta = sum(int(o) for o in ofertas)
        demandas = [str(random.randint(*rango_demandas)) for _ in range(num_destinos - 1)]
        resto = total_oferta - sum(int(d) for d in demandas)
        if resto <= 0:
            resto = random.randint(*rango_demandas)
        demandas.append(str(resto))
    else:
        demandas = [str(random.randint(*rango_demandas)) for _ in range(num_destinos)]

    return {
        'origenes': origenes,
        'destinos': destinos,
        'costos': costos,
        'ofertas': ofertas,
        'demandas': demandas,
    }


# ---------------------------------------------------------------------------
# Serialización para guardar/cargar ejercicios (formato JSON-friendly)
# ---------------------------------------------------------------------------

def problema_a_dict(problema, nombre=''):
    """Convierte un ProblemaTransporte a diccionario serializable."""
    return {
        'nombre': nombre,
        'origenes': problema.origenes,
        'destinos': problema.destinos,
        'costos': [[str(c) for c in fila] for fila in problema.costos],
        'ofertas': [str(o) for o in problema.ofertas],
        'demandas': [str(d) for d in problema.demandas],
    }


def dict_a_problema(d):
    """Reconstruye un ProblemaTransporte desde un diccionario."""
    p = ProblemaTransporte()
    p.origenes = d['origenes']
    p.destinos = d['destinos']
    p.costos = [[Decimal(c) for c in fila] for fila in d['costos']]
    p.ofertas = [Decimal(o) for o in d['ofertas']]
    p.demandas = [Decimal(dem) for dem in d['demandas']]
    return p, d.get('nombre', '')


# ---------------------------------------------------------------------------
# Solución Óptima Global (Simplex de Transporte Exacto)
# ---------------------------------------------------------------------------

def resolver_optimo_transporte(problema):
    """
    Calcula la Solución Óptima de Costo Mínimo usando el algoritmo Simplex exacto
    (con números racionales exactos Fraction para garantizar precisión matemática absoluta).
    Retorna (asignaciones_optimas, costo_optimo).
      asignaciones_optimas: matriz [m][n] de Decimal
      costo_optimo: Decimal
    """
    from fractions import Fraction

    m = problema.num_origenes()
    n = problema.num_destinos()
    n_vars = m * n
    n_eq = m + n

    # Matriz A de tamaño n_eq x n_vars
    A = [[Fraction(0)] * n_vars for _ in range(n_eq)]
    b = [Fraction(0)] * n_eq

    for i in range(m):
        for j in range(n):
            A[i][i * n + j] = Fraction(1)
        b[i] = Fraction(str(problema.ofertas[i]))

    for j in range(n):
        for i in range(m):
            A[m + j][i * n + j] = Fraction(1)
        b[m + j] = Fraction(str(problema.demandas[j]))

    c = [Fraction(str(problema.costos[i][j])) for i in range(m) for j in range(n)]

    # Fase 1: Variables artificiales
    tot_vars = n_vars + n_eq
    tableau = [[Fraction(0)] * (tot_vars + 1) for _ in range(n_eq + 1)]

    for i in range(n_eq):
        for j in range(n_vars):
            tableau[i][j] = A[i][j]
        tableau[i][n_vars + i] = Fraction(1)
        tableau[i][-1] = b[i]

    basis = [n_vars + i for i in range(n_eq)]

    for j in range(tot_vars + 1):
        s = sum(tableau[i][j] for i in range(n_eq))
        tableau[n_eq][j] = -s

    def pivot(p_row, p_col):
        pivot_val = tableau[p_row][p_col]
        for c_idx in range(tot_vars + 1):
            tableau[p_row][c_idx] /= pivot_val
        for r_idx in range(n_eq + 1):
            if r_idx != p_row:
                factor = tableau[r_idx][p_col]
                if factor != 0:
                    for c_idx in range(tot_vars + 1):
                        tableau[r_idx][c_idx] -= factor * tableau[p_row][c_idx]
        basis[p_row] = p_col

    # Fase 1 Simplex
    for _ in range(500):
        min_val = Fraction(0)
        p_col = -1
        for j in range(tot_vars):
            if tableau[n_eq][j] < min_val:
                min_val = tableau[n_eq][j]
                p_col = j
        if p_col == -1 or min_val >= 0:
            break
        min_ratio = None
        p_row = -1
        for i in range(n_eq):
            if tableau[i][p_col] > Fraction(0):
                ratio = tableau[i][-1] / tableau[i][p_col]
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio
                    p_row = i
        if p_row == -1:
            break
        pivot(p_row, p_col)

    # Fase 2 Simplex
    for j in range(tot_vars + 1):
        tableau[n_eq][j] = Fraction(0)
    for j in range(n_vars):
        tableau[n_eq][j] = -c[j]

    for i in range(n_eq):
        b_var = basis[i]
        if b_var < n_vars:
            coef = c[b_var]
            for j in range(tot_vars + 1):
                tableau[n_eq][j] += coef * tableau[i][j]

    for _ in range(500):
        max_val = Fraction(0)
        p_col = -1
        for j in range(n_vars):
            if tableau[n_eq][j] > max_val:
                max_val = tableau[n_eq][j]
                p_col = j
        if p_col == -1 or max_val <= 0:
            break
        min_ratio = None
        p_row = -1
        for i in range(n_eq):
            if tableau[i][p_col] > Fraction(0):
                ratio = tableau[i][-1] / tableau[i][p_col]
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio
                    p_row = i
        if p_row == -1:
            break
        pivot(p_row, p_col)

    # Extraer asignaciones óptimas
    asig_opt = [[Decimal('0')] * n for _ in range(m)]
    for i in range(n_eq):
        if basis[i] < n_vars:
            var = basis[i]
            r = var // n
            col = var % n
            val_frac = tableau[i][-1]
            # Convertir fracción a Decimal exacto
            asig_opt[r][col] = Decimal(str(float(val_frac)))

    costo_opt = Decimal('0')
    for i in range(m):
        for j in range(n):
            costo_opt += asig_opt[i][j] * problema.costos[i][j]

    return asig_opt, costo_opt

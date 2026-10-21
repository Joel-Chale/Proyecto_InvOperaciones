# Método de la Esquina Noroeste
## Investigación de Operaciones — Problemas de Transporte

Aplicación gráfica completa en Python para resolver problemas de transporte
usando el **Método de la Esquina Noroeste**.

---

## Requisitos

- **Python 3.8 o superior** (recomendado: Python 3.10+)
- **Tkinter** (incluido por defecto en Python para Windows y macOS)
- No requiere librerías externas adicionales

### Verificar Python

```
python --version
```

---

## Cómo ejecutar

### Opción 1 — Doble clic (Windows)
Haga doble clic en el archivo **`Iniciar.bat`**

### Opción 2 — Terminal
```bash
cd transporte_io
python main.py
```

---

## Estructura del proyecto

```
transporte_io/
├── main.py            # Ventana principal y coordinador de la UI
├── logica.py          # Motor matemático (validación, balance, algoritmo, costos)
├── estilos.py         # Paleta de colores, fuentes y estilos ttk
├── widgets_tabla.py   # Widgets reutilizables (tabla editable, tabla de asignaciones)
├── Iniciar.bat        # Lanzador para Windows
└── README.md          # Este archivo
```

---

## Cómo usar el programa

### Paso 1 — Configurar el problema
- Establezca el número de **orígenes** y **destinos** con los controles de la izquierda.
- Haga clic en **"🔧 Crear tabla"**.

### Paso 2 — Ingresar datos
En la tabla que aparece a la derecha:
- Escriba los **costos unitarios** de transporte en cada celda.
- Escriba la **oferta** de cada origen en la columna derecha.
- Escriba la **demanda** de cada destino en la fila inferior.
- Puede editar directamente los **nombres** de orígenes y destinos.

El programa actualiza automáticamente los totales y el estado del balance.

### Paso 3 — Verificar balance / Resolver
- Haga clic en **"✔ Verificar balance"** para ver el análisis antes de resolver.
- O directamente en **"▶ Resolver ejercicio"** para calcular todo automáticamente.

### Paso 4 — Explorar el procedimiento
En la pestaña **"Resolución paso a paso"**:
- Use **"Paso siguiente ▶"** y **"◀ Paso anterior"** para navegar.
- Use **"⚡ Mostrar solución completa"** para ver directamente los resultados.

### Paso 5 — Ver resultados
En la pestaña **"Resultados y costo"** encontrará:
- Tabla final de asignaciones con colores.
- Desglose de cada asignación.
- Fórmula del costo total desarrollada.
- Advertencias sobre degeneración si corresponde.

---

## Funciones disponibles

| Botón | Función |
|---|---|
| 🚀 RESOLVER EJERCICIO | Resuelve directamente en 1 clic aplicando la Esquina Noroeste |
| ⚖ Balancear / Verificar | Comprueba si el problema está balanceado y agrega ficticios si aplica |
| 🎯 Evaluación de Optimalidad | Compara la Esquina Noroeste con la Solución Óptima de Costo Mínimo |
| 🔍 Ver Asignación Óptima | Muestra la distribución de costo mínimo absoluto y el porcentaje de ahorro |
| 🔧 Crear / Ajustar tabla | Genera la tabla con las dimensiones indicadas |
| + / - Origen o Destino | Añade o quita filas/columnas rápidamente conservando datos |
| ⭐ Cargar Ejemplo | Carga un problema balanceado clásico listo para resolver |
| 🎲 Datos Aleatorios | Genera un problema con valores configurables |
| 🧹 Limpiar Tabla | Borra los campos de costo, oferta y demanda (pide confirmación) |
| 💾 Guardar / 📂 Abrir | Guarda y carga ejercicios en formato JSON |
| 📤 Exportar TXT / CSV | Exporta el reporte paso a paso y la tabla en CSV para Excel |
| ❓ Ayuda | Guía completa y conceptos teóricos de Investigación de Operaciones |

---

## Colores de la tabla

| Color | Significado |
|---|---|
| 🟡 Amarillo claro | Celda en proceso actualmente |
| 🟢 Verde claro | Celda con asignación positiva |
| ⬜ Gris claro | Fila/columna ya satisfecha o cero |
| 🟣 Morado claro | Elemento ficticio (para balance) |
| 🔵 Azul oscuro | Encabezados de la tabla |

---

## Ejercicio de ejemplo incluido

El botón **"⭐ Ejemplo automático"** carga el siguiente problema:

|         | Ciudad 1 | Ciudad 2 | Ciudad 3 | Ciudad 4 | Oferta |
|---------|----------|----------|----------|----------|--------|
| Fábrica A | 2 | 3 | 1 | 5 | 120 |
| Fábrica B | 7 | 3 | 4 | 6 | 80 |
| Fábrica C | 8 | 5 | 2 | 3 | 100 |
| **Demanda** | 150 | 70 | 60 | 20 | 300 |

**Solución con Esquina Noroeste:**
- Fábrica A → Ciudad 1: 120 unidades
- Fábrica B → Ciudad 1: 30 unidades
- Fábrica B → Ciudad 2: 50 unidades
- Fábrica C → Ciudad 2: 20 unidades
- Fábrica C → Ciudad 3: 60 unidades
- Fábrica C → Ciudad 4: 20 unidades
- **Costo total = 880**

---

## Notas importantes

> **El Método de la Esquina Noroeste obtiene una solución básica factible INICIAL.**
> **NO garantiza el costo mínimo.** Para la solución óptima se requieren
> métodos adicionales como MODI (Modified Distribution Method) o Stepping-Stone.

---

## Formatos de archivo

- **Guardar/Abrir:** formato JSON (`.json`) — incluye todos los datos del problema.
- **Exportar TXT:** procedimiento completo paso a paso + costo total.
- **Exportar CSV:** tabla de asignaciones + desglose de costos (compatible con Excel).

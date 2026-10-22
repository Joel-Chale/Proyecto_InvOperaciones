# 🚚 Método de la Esquina Noroeste
## Investigación de Operaciones — Problemas de Transporte

Aplicación gráfica moderna, intuitiva y completa para resolver problemas de transporte mediante el **Método de la Esquina Noroeste**, con explicación pedagógica paso a paso y comparador de **solución óptima de costo mínimo**.

---

## ⚡ Ejecución rápida (Sin instalar Python)

El programa cuenta con un ejecutable independiente compilado para Windows:

* **Ruta del ejecutable:** `dist/EsquinaNoroeste.exe`
* **Doble clic y listo:** No requiere instalar Python, ni librerías adicionales. Es 100% portátil.

---

## 💻 Requisitos para desarrolladores (Código fuente)

Si deseas ejecutar o modificar el código fuente en Python:
- **Python 3.8 o superior** (probado y optimizado en Python 3.13)
- **Tkinter** (incluido por defecto en las instalaciones oficiales de Python)
- Sin dependencias de terceros obligatorias (utiliza librerías estándar: `decimal`, `fractions`, `json`, `csv`).

### Ejecución desde consola o script:
```bash
# Opción A: Archivo por lotes (Windows)
Iniciar.bat

# Opción B: Terminal
python main.py
```

---

## 📁 Estructura del proyecto

```
transporte_io/
├── dist/
│   └── EsquinaNoroeste.exe    # Ejecutable portátil para Windows (sin dependencias)
├── main.py                    # Ventana principal, navegación por pestañas y controlador
├── logica.py                  # Motor matemático (validación, balanceo, esquina noroeste y solver óptimo)
├── widgets_tabla.py           # Componentes gráficos de tablas (TablaCostos y TablaAsignaciones)
├── estilos.py                 # Paleta de colores, tipografías y scrollframes responsivos
├── esquina_noroeste.spec      # Configuración de compilación de PyInstaller
├── Iniciar.bat                # Lanzador directo para Windows
└── README.md                  # Documentación del proyecto
```

---

## 🚀 Cómo usar el programa

### 1. Configurar dimensiones y datos
* En la pestaña **"Datos del problema"**, define la cantidad de orígenes y destinos (o usa los botones `+ / -`).
* Haz clic en **"🔧 Crear / Ajustar tabla"**.
* Escribe los costos unitarios en cada celda, las ofertas en la columna derecha y las demandas en la fila inferior.
* Los nombres de orígenes y destinos se pueden editar haciendo clic sobre ellos.
* La esquina inferior derecha muestra en tiempo real la relación `Demanda \ Oferta`.

### 2. Resolver el problema
* Haz clic en **"▶ RESOLVER EJERCICIO"** (botón directo en la barra superior o en el panel lateral).
* Si el problema no está balanceado, el sistema agrega automáticamente un **Origen o Destino Ficticio** con costo cero e informa el ajuste realizado.

### 3. Procedimiento paso a paso
* En la pestaña **"Resolución paso a paso"**, navega con **"Paso siguiente ▶"** y **"◀ Paso anterior"**.
* En cada celda de la tabla interactiva se visualiza:
  * El costo unitario original ingresado (arriba a la derecha: `c: X`).
  * La cantidad asignada en el paso (en el centro en grande).
  * La celda activa destacada en color amarillo.
  * La explicación textual con palabras sencillas de por qué se avanza a la siguiente fila o columna.

### 4. Resultados y Análisis de Optimalidad
* En la pestaña **"Resultados y costo"** encontrarás:
  * Tabla final de asignaciones completa con totales en formato `Demanda \ Oferta`.
  * Desglose de cada envío realizado y fórmula matemática expandida del costo total.
  * **🎯 Evaluación de Optimalidad:** Compara el costo de la Esquina Noroeste con la **Solución Óptima Real de Costo Mínimo**. Si existe una distribución con menor costo, te indica el ahorro posible y te permite hacer clic en **"🔍 Ver Tabla de Asignaciones Óptimas"** para examinarla.

---

## 🎛️ Funciones y herramientas disponibles

| Herramienta | Descripción |
|---|---|
| **▶ RESOLVER EJERCICIO** | Resuelve el problema en 1 clic aplicando la Esquina Noroeste y balanceo automático. |
| **⚖ Balancear** | Muestra el análisis previo de oferta total vs. demanda total y tablas balanceadas. |
| **🎯 Evaluación de Optimalidad** | Verifica si la solución inicial obtenida ya es óptima o cuánto puede reducirse el costo. |
| **🔍 Ver Asignación Óptima** | Despliega en ventana emergente la matriz de distribución óptima absoluta. |
| **⭐ Cargar Ejemplo** | Carga al instante un problema de transporte clásico balanceado listo para probar. |
| **🎲 Datos Aleatorios** | Ventana emergente con configuración de rangos y botón fijo `🎲 GENERAR DATOS`. |
| **🧹 Limpiar Tabla** | Borra todos los valores numéricos ingresados pidiendo confirmación. |
| **💾 Guardar / 📂 Abrir** | Almacena y recupera ejercicios completos en formato estructurado `.json`. |
| **📤 Exportar TXT / CSV** | Genera reportes de texto detallados paso a paso o archivos CSV compatibles con Microsoft Excel. |
| **❓ Ayuda** | Guía teórica y manual de usuario integrado en la aplicación. |

---

## 🎨 Código de colores en las tablas

| Muestra visual | Color | Significado |
|---|---|---|
| 🟡 | **Amarillo suave** | Celda activa en proceso de asignación actual. |
| 🟢 | **Verde claro** | Celda con asignación de unidades confirmada. |
| ⬜ | **Gris claro / Blanco** | Celda sin asignación o ruta agotada. |
| 🟣 | **Morado claro** | Origen o Destino Ficticio agregado para balancear. |
| 🔵 | **Azul oscuro** | Encabezados de tabla, columna de oferta y fila de demanda. |

---

## 📝 Ejemplo resuelto incluido

Al presionar el botón **"⭐ Cargar Ejemplo"** se carga el siguiente caso balanceado:

| Origen \ Destino | Ciudad 1 | Ciudad 2 | Ciudad 3 | Ciudad 4 | Oferta |
|---|---|---|---|---|---|
| **Fábrica A** | 2 | 3 | 1 | 5 | **120** |
| **Fábrica B** | 7 | 3 | 4 | 6 | **80** |
| **Fábrica C** | 8 | 5 | 2 | 3 | **100** |
| **Demanda** | **150** | **70** | **60** | **20** | **300 \ 300** |

* **Solución por Esquina Noroeste:**
  * Fábrica A → Ciudad 1: 120 unidades (Costo: 120 × 2 = 240)
  * Fábrica B → Ciudad 1: 30 unidades (Costo: 30 × 7 = 210)
  * Fábrica B → Ciudad 2: 50 unidades (Costo: 50 × 3 = 150)
  * Fábrica C → Ciudad 2: 20 unidades (Costo: 20 × 5 = 100)
  * Fábrica C → Ciudad 3: 60 unidades (Costo: 60 × 2 = 120)
  * Fábrica C → Ciudad 4: 20 unidades (Costo: 20 × 3 = 60)
  * **Costo Total Esquina Noroeste = 880**
* **Comparativa Óptima:**
  * **Costo Mínimo Real = 860** (Ahorro potencial: 20 unidades / 2.3%).

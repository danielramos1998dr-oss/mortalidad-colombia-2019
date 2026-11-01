# Mortalidad en Colombia · 2019

## Introducción del proyecto
Aplicación educativa de análisis descriptivo de defunciones no fetales de Colombia en 2019. Desarrollada con Python, Dash y Plotly a partir de los tres anexos suministrados en la actividad. Contiene siete elementos visuales, filtros por departamento, periodo mensual y sexo, y descarga de la tabla de causas.

**Estado:** código y pruebas locales completados. Pendientes: creación del repositorio GitHub, despliegue público en Render, verificación de la interfaz Dash en navegador y capturas de la aplicación desplegada. No se han creado URL públicas ni se afirma que la entrega académica esté terminada.

## Objetivo
Explorar la distribución territorial, temporal, por causa, sexo y ciclo de vida de 244.355 defunciones registradas, mediante visualizaciones interactivas reproducibles. No estimar riesgos poblacionales ni establecer relaciones causales.

## Integrantes y enlaces de entrega
- Integrante 1: [nombre completo por confirmar]
- Otros integrantes: [completar si corresponde; máximo cuatro]
- Aplicación PaaS: [pendiente del despliegue]
- Repositorio GitHub: [pendiente de creación]

Cada integrante debe presentar su entrega individual en el aula virtual.

## Estructura del proyecto
| Ruta | Función |
|---|---|
| `app.py` | Interfaz Dash, gráficos, callbacks y servidor WSGI `server`. |
| `analysis.py` | Filtros, agrupaciones y rankings reutilizables. |
| `prepare_data.py` | Reconstrucción de los CSV a partir de los Excel. |
| `requirements.txt` | Dependencias con versiones fijadas. |
| `render.yaml` | Configuración de despliegue en Render. |
| `assets/style.css` | Diseño responsive. |
| `assets/world_110m.json` | Cartografía general distribuida por Plotly (Natural Earth). |
| `data/raw/` | Los tres Excel originales, sin modificaciones. |
| `data/mortalidad.csv.gz` | Campos analíticos normalizados; 244.355 filas. |
| `data/causas.csv` | Catálogo de códigos completos de tres/cuatro caracteres. |
| `data/departamentos.csv` | Coordenadas de capitales desde DIVIPOLA. |
| `data/auditoria.json` | Totales, cobertura de cruces y SHA-256 de los originales. |
| `tests/test_analysis.py` | Pruebas de datos y callbacks. |
| `docs/Informe_interactivo.html` | Informe nacional interactivo con interpretación; no sustituye Dash. |
| `docs/plotly.min.js`, `docs/world_110m.json` | Recursos locales del informe. |

## Requisitos y software
Python 3.11 recomendado; Dash 3.2.0, Plotly 6.3.0, Pandas 2.2.3, Openpyxl 3.1.5 y Gunicorn 23.0.0. Gunicorn se usa en Linux/Render; en Windows se ejecuta `python app.py`. Git y una cuenta GitHub para el repositorio; cuenta Render para publicar. No se requiere Node para esta aplicación.

## Instalación
Extraer el ZIP y abrir una terminal en la carpeta que contiene `app.py`. Si ya se ha publicado el repositorio:

```bash
git clone https://github.com/USUARIO/REPOSITORIO.git
cd REPOSITORIO
```

Reemplazar `USUARIO/REPOSITORIO` por la dirección real; no es un repositorio existente.

### Windows PowerShell
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abrir http://127.0.0.1:8050. No hace falta activar el entorno ni cambiar la política de ejecución de PowerShell.

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Los CSV ya están preparados. Para reconstruirlos tras cambiar los originales:
```bash
python prepare_data.py
python -m unittest discover -s tests -v
```
No regenerar los CSV mientras corre el servidor: detenerlo, regenerar, probar y volver a iniciar.

### Abrir el informe complementario
Desde la raíz del proyecto:
```bash
python -m http.server 8000 --directory docs
```
Abrir http://127.0.0.1:8000/Informe_interactivo.html. Con doble clic funcionan los gráficos no geográficos; el mapa necesita HTTP para leer su fondo local. Mantener `plotly.min.js` y `world_110m.json` junto al HTML.

## Metodología y calidad
- Cada fila se cuenta como una defunción. No se eliminan aparentes duplicados porque no hay identificador único de defunción.
- Se comprueba que todas las filas sean de 2019 y que departamento + municipio coincida con el código DANE de cinco dígitos.
- Cruce municipal muchos a uno, sin multiplicar filas. Todos los registros se homologaron.
- Causas por código completo: por ejemplo `I219` y `C61`. Se usan ambas columnas de categorías del catálogo, sin confundir códigos válidos de tres caracteres con códigos faltantes. No hubo registros sin descripción.
- La geografía se interpreta como lugar de ocurrencia de la defunción según la estructura EEVV; el anexo académico renombra y reduce las variables. No tiene residencia ni la ubicación específica del hecho violento.
- X95 significa agresión con disparo de otras armas de fuego y las no especificadas. Se incluyen todos sus subcódigos mediante prefijo `X95`; no todos los homicidios ni todas las armas de fuego.
- Sin población expuesta no se calcula una tasa. El gráfico circular representa los diez municipios/áreas con menor número **positivo** de registros, no un índice de mortalidad. No se interpreta ausencia de registros como cero real.
- Empates en rankings: código DANE ascendente. Los nombres incluyen departamento para evitar ambigüedad.
- Sexo: 1 masculino, 2 femenino, 3 indeterminado. Se conserva la tercera categoría.
- El gráfico de edades es un histograma de frecuencias preagrupadas representado mediante barras contiguas de categorías ordenadas; no se aplica binning automático a los códigos ordinales ni se presenta densidad por año de edad.

### Agrupación de edades de la actividad
| Categoría | Códigos | Rango |
|---|---|---|
| Mortalidad neonatal | 0–4 | Menor de 1 mes |
| Mortalidad infantil | 5–6 | 1–11 meses |
| Primera infancia | 7–8 | 1–4 años |
| Niñez | 9–10 | 5–14 años |
| Adolescencia | 11 | 15–19 años |
| Juventud | 12–13 | 20–29 años |
| Adultez temprana | 14–16 | 30–44 años |
| Adultez intermedia | 17–19 | 45–59 años |
| Vejez | 20–24 | 60–84 años |
| Longevidad / Centenarios | 25–28 | 85–100+ años |
| Edad desconocida | 29 | Sin información |

El código 4 incluye 28–29 días. Se conserva la tabla solicitada, pero sus etiquetas neonatal e infantil no deben confundirse con definiciones epidemiológicas: la mortalidad neonatal estricta es menor de 28 días y la infantil abarca menores de un año.

## Visualizaciones y explicación de resultados
Los valores siguientes corresponden a Colombia, enero–diciembre, todos los sexos. Los filtros pueden cambiar los resultados.

| Elemento | Hallazgo e interpretación |
|---|---|
| Mapa | Bogotá D. C. 38.760, Antioquia 34.473 y Valle del Cauca 28.443 encabezan el volumen. Mapa de burbujas por departamento ubicado en capitales; no es un mapa de límites departamentales. No compara riesgos. |
| Línea mensual | Diciembre 21.678; febrero 17.974. Diferencia: 3.704. No ajustado por duración de los meses; no demuestra estacionalidad con un solo año. |
| Barras X95 | Total nacional 9.273. Cali 971, Bogotá 601, Medellín 428, Barranquilla 260 y Cúcuta 206. Es un ranking de conteos de X95, no de toda la violencia. |
| Circular | Diez territorios con un registro cada uno; cada uno aporta 10 % del subtotal seleccionado. Empates resueltos por DANE. Incluye áreas no municipalizadas del catálogo. |
| Tabla de causas | I219 ocupa el primer lugar con 35.088 registros (14,36 %). Se mantienen códigos individuales; no se agrupan todas las enfermedades cardiovasculares. |
| Barras apiladas | Masculino 134.573 (55,07 %), femenino 109.689 (44,89 %), indeterminado 93 (0,04 %). La comparación usa conteos, no tasas específicas por sexo. |
| Edades | 60–84 años: 115.453 (47,25 %). Edad desconocida: 23. Intervalos de distinta amplitud; no interpretar alturas como riesgo por edad. |

El informe HTML incluye gráficos e interpretaciones completas. Las capturas definitivas de la aplicación Dash aún deben obtenerse después de su publicación. Guardarlas en `docs/capturas/` y agregarlas aquí con Markdown, por ejemplo `![Mapa del dashboard](docs/capturas/01_mapa.png)`, solo cuando exista el archivo real.

Capturas que faltan: vista general con filtros, mapa y línea; ranking X95 y circular; tabla de causas; barras por sexo; edades; una vista filtrada (por ejemplo Nariño). Las capturas de un informe HTML o de figuras exportadas no deben presentarse como prueba de una aplicación Dash desplegada.

## Despliegue en Render
Estos son pasos preparados, todavía **no ejecutados en una cuenta Render**:

1. Crear un repositorio GitHub y subir el contenido de esta carpeta a su raíz. Incluir datos procesados, `assets/`, código, requisitos y README. No subir `.venv`, credenciales ni cachés. Los Excel permiten reproducir el procesamiento.
2. En Render elegir **New → Web Service** y conectar el repositorio.
3. Elegir Python, rama `main` (o la rama real), y raíz del repositorio como directorio de trabajo.
4. Build command: `pip install -r requirements.txt`.
5. Start command: `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`.
6. Establecer `PYTHON_VERSION=3.11.11`. Health check: `/health`. El archivo `render.yaml` contiene estos valores para despliegue mediante Blueprint.
7. Elegir el plan revisando las condiciones de la cuenta. No se ha contratado ningún plan ni asumido un costo.
8. Publicar y esperar que Render confirme que el servicio está activo. Abrir su URL pública en ventana privada sin iniciar sesión.
9. Comprobar los siete elementos, filtros de departamento/sexo/mes, Restablecer, descarga CSV y mapa. `/health` debe responder `status: ok` y `registros: 244355`.
10. Guardar capturas reales, actualizar este README con ambas URL y completar integrantes. Probar nuevamente el enlace antes de entregar.

Los datos se cargan una vez al iniciar cada proceso; el CSV comprimido evita leer los Excel durante cada visita. No se necesita base de datos ni almacenamiento persistente adicional para esta versión.

## Validación realizada y límites
Cinco pruebas automatizadas comprueban particiones y totales, fronteras de edad, filtros, rankings, endpoints HTTP y generación/serialización de figuras en callbacks nacionales, filtrados y sin datos. Se revisó el informe HTML en navegador. La vista previa gestionada no dispone de Python, por lo que no se verificó aún el recorrido completo de controles Dash en navegador ni el servicio PaaS.

## Fuentes y documentación
- [DANE EEVV 2019](https://microdatos.dane.gov.co/index.php/catalog/696).
- [Diccionario GRU_ED1](https://microdatos.dane.gov.co/index.php/catalog/696/variable/F23/V1350?name=GRU_ED1).
- [Diccionario SEXO](https://microdatos.dane.gov.co/index.php/catalog/696/variable/F23/V1348?name=SEXO).
- [Publicación Dash](https://dash.plotly.com/deployment).
- [Despliegue de servidores Flask/WSGI en Render](https://render.com/docs/deploy-flask).
- [Mapas de puntos Plotly](https://plotly.com/python/scatter-plots-on-maps/).
- Fondo de mapa: [world_110m.json distribuido por Plotly](https://cdn.plot.ly/world_110m.json). Datos cartográficos generales de Natural Earth; no límites departamentales DIVIPOLA.
- Insumos analíticos: los tres archivos Excel proporcionados en la actividad. Los módulos RED6 no fueron suministrados y no se afirma haberlos revisado.

## Captura del informe complementario
Esta captura corresponde al informe HTML generado con las figuras de Dash; no demuestra un despliegue público ni reemplaza las capturas pendientes de la aplicación.

![Informe complementario](docs/Informe_captura.jpg)

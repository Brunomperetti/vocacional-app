# vocacional-app

Base inicial de una plataforma online de orientación vocacional para estudiantes. La aplicación está preparada para crecer hacia un test con preguntas, scoring RIASEC y recomendación de carreras.

## Stack

- Python
- FastAPI
- Jinja2 Templates
- SQLAlchemy
- PostgreSQL compatible con Render
- HTML/CSS/JS simple

## Estructura principal

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── data/
├── routes/
├── services/
├── templates/
└── static/
```

## Requisitos

- Python 3.11+
- pip

## Configuración local

1. Crear y activar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno opcionales:

```bash
cp .env.example .env
```

Si `DATABASE_URL` no está definida, la app usa SQLite local en `vocacional_dev.db`.

También se puede configurar `DONATION_URL` con un link externo de aporte voluntario (por ejemplo, un link de Mercado Pago). Cuando esta variable existe, la app muestra un botón de colaboración en el resultado y un enlace discreto en el footer. El aporte es completamente opcional: el test y el resultado siguen siendo gratuitos y no se bloquea ninguna funcionalidad si la variable no está configurada.

4. Ejecutar la aplicación:

```bash
uvicorn app.main:app --reload
```

5. Abrir en el navegador:

- Landing: <http://127.0.0.1:8000/>
- Inicio del test: <http://127.0.0.1:8000/test>
- Resultado demo: <http://127.0.0.1:8000/resultado/demo>
- Admin temporal: <http://127.0.0.1:8000/admin>
- Health check: <http://127.0.0.1:8000/health>

## Banco inicial de preguntas RIASEC

La app ya incluye un banco inicial de 36 preguntas RIASEC en `app/data/questions.py`, distribuido en 6 preguntas por dimensión: Realista, Investigativo, Artístico, Social, Emprendedor y Convencional.

La ruta `/test` ahora funciona como pantalla de inicio del test y solicita datos iniciales opcionales del participante: nombre, WhatsApp, edad, situación actual y ubicación. Se usa WhatsApp opcional en lugar de email; si se completa, solo se valida y normaliza para guardarlo temporalmente en sesión, y no se muestra en el resultado por privacidad. Estos datos se usan únicamente para personalizar el resultado final. Desde allí el usuario ingresa a un flujo tipo wizard de 6 etapas en `/test/paso/{step}`: Realista, Investigativo, Artístico, Social, Emprendedor y Convencional. Cada etapa muestra solo las 6 preguntas de esa dimensión con escala Likert de 1 a 5, valida que todas estén respondidas y avanza al paso siguiente hasta completar las 36 respuestas.

El sistema calcula puntajes reales por dimensión, convierte cada puntaje a porcentaje sobre un máximo de 30 puntos, ordena las dimensiones principales y arma un código vocacional de 3 letras. Además, incluye una base inicial de al menos 40 carreras y oficios en `app/data/careers.py`, cada una con descripción, área, tipo de formación, duración, skills y perfil RIASEC propio.

Las recomendaciones del resultado comparan el perfil RIASEC porcentual del usuario contra el perfil RIASEC de cada carrera, calculan una compatibilidad de 0 a 100 y muestran las mejores opciones ordenadas de mayor a menor compatibilidad.

La pantalla final también incluye un resumen interpretativo del perfil, fortalezas principales, ambientes recomendados donde el estudiante podría rendir mejor y próximos pasos accionables para investigar carreras, comparar planes de estudio y conversar con referentes. Estos textos son orientativos, no clínicos, y acompañan la recomendación de carreras por compatibilidad RIASEC sin reemplazar una evaluación profesional.

Desde la pantalla final, el usuario puede descargar un informe PDF del resultado con el código vocacional, resumen, scoring RIASEC, dimensiones principales, fortalezas, ambientes recomendados, hasta 6 carreras sugeridas y próximos pasos. El PDF se genera en memoria desde los datos del resultado guardados en la sesión actual (`request.session["last_result"]`) y se entrega desde `/resultado/pdf` como archivo descargable; no se guarda en disco.

Durante el wizard, las respuestas acumuladas y los datos iniciales opcionales del participante se guardan temporalmente en la sesión HTTP mediante `SessionMiddleware`; `SESSION_SECRET` puede configurarse por variable de entorno y, si no existe, se usa un valor local de desarrollo. La navegación pública muestra solo el acceso al test y oculta accesos internos o demo como `/resultado/demo` y `/admin`, aunque esas rutas siguen disponibles si se accede directamente.

La monetización voluntaria se controla con `DONATION_URL`: si se define, el resultado final y el footer muestran enlaces a una página externa de aporte; si se omite, esos elementos no se renderizan y la aplicación funciona igual. No hay integración con API de pagos, checkout interno, pagos obligatorios, guardado de datos de pago, login ni base de datos adicional para esta funcionalidad.

En esta etapa las respuestas, los datos iniciales opcionales y los resultados todavía no se guardan en base de datos: solo viven en sesión mientras el usuario completa el test. El informe PDF también depende de esa sesión actual y no queda almacenado en base de datos ni en archivos persistentes. No se crea lógica adicional de persistencia para el test.

## Base de datos

La conexión se configura con la variable `DATABASE_URL`.

- Desarrollo sin configuración: `sqlite:///./vocacional_dev.db`
- Producción Render/PostgreSQL: usar la URL provista por Render

La app normaliza URLs `postgres://` y `postgresql://` para usar el driver `psycopg` de SQLAlchemy.

## Deploy en Render

El archivo `render.yaml` incluye una configuración inicial para:

- Servicio web Python
- Instalación con `pip install -r requirements.txt`
- Inicio con `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Base de datos PostgreSQL administrada por Render

## Estado actual

Incluye la base funcional inicial, el banco de 36 preguntas RIASEC, el test por etapas desde `/test`, el cálculo real de scoring RIASEC en memoria, insights interpretativos del resultado final y una recomendación inicial de carreras por compatibilidad RIASEC. Todavía no contiene guardado de respuestas del test en base de datos, login real ni machine learning.

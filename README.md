# Vocación360

Vocación360 es la base inicial de una plataforma online de orientación vocacional para estudiantes. La aplicación está preparada para crecer hacia un test con preguntas, scoring RIASEC y recomendación de carreras.

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

`APP_NAME` permite configurar el nombre público usado en templates y en el informe PDF. Si no se define, el nombre público por default es `Vocación360`.

También se puede configurar `DONATION_URL` con un link externo de aporte voluntario (por ejemplo, un link de Mercado Pago). Cuando esta variable existe, la app muestra un botón de colaboración en el resultado y un enlace discreto en el footer. El aporte es completamente opcional: el test y el resultado siguen siendo gratuitos y no se bloquea ninguna funcionalidad si la variable no está configurada.

También se puede configurar `PUBLIC_APP_URL` con la URL pública de la aplicación (por ejemplo, la URL de Render). Si existe, se usa para armar el enlace compartido por WhatsApp; si se omite, la app usa la URL del request actual para apuntar a `/test`.

El panel `/admin` requiere login y se protege con las variables de entorno `ADMIN_USERNAME` y `ADMIN_PASSWORD`. No hay credenciales hardcodeadas ni usuarios en base de datos todavía. Si alguna de estas variables falta, el formulario informa que el acceso admin no está configurado y no permite ingresar. En Render deben agregarse desde **Environment Variables** junto con el resto de la configuración del servicio.

4. Ejecutar la aplicación:

```bash
uvicorn app.main:app --reload
```

5. Abrir en el navegador:

- Landing: <http://127.0.0.1:8000/>
- Inicio del test: <http://127.0.0.1:8000/test>
- Resultado demo: <http://127.0.0.1:8000/resultado/demo>
- Privacidad: <http://127.0.0.1:8000/privacidad>
- Aviso legal: <http://127.0.0.1:8000/aviso-legal>
- Admin con login: <http://127.0.0.1:8000/admin>
- Health check: <http://127.0.0.1:8000/health>

## Medición opcional de marketing

La app puede activar medición básica de lanzamiento sin cambiar el flujo del test ni guardar eventos en la base de datos. Las variables son opcionales y, si se omiten o quedan vacías, la aplicación funciona igual y no renderiza scripts de terceros.

- `GA_MEASUREMENT_ID` activa Google Analytics 4 mediante el tag básico de `gtag.js`.
- `META_PIXEL_ID` activa Meta Pixel con `PageView` y eventos personalizados front-end.

Eventos disponibles desde el front-end:

- `view_landing`: carga de la landing pública.
- `start_test`: click o envío para comenzar el test.
- `test_step_view`: carga de cada paso del wizard, con número de paso y dimensión RIASEC.
- `complete_test`: carga de un resultado real; no se dispara en `/resultado/demo`.
- `download_pdf`: click en descarga del informe PDF.
- `share_whatsapp`: click en compartir el test por WhatsApp.
- `donation_click`: click en el aporte voluntario.

## Banco inicial de preguntas RIASEC

La app ya incluye un banco inicial de 36 preguntas RIASEC en `app/data/questions.py`, distribuido en 6 preguntas por dimensión: Realista, Investigativo, Artístico, Social, Emprendedor y Convencional.

La ruta `/test` ahora funciona como pantalla de inicio del test y solicita datos iniciales opcionales del participante: nombre, WhatsApp, edad, situación actual y ubicación. Se usa WhatsApp opcional en lugar de email; si se completa, solo se valida y normaliza para guardarlo temporalmente en sesión, y no se muestra en el resultado por privacidad. Además, antes de iniciar se requiere aceptar un consentimiento de uso de datos: el test sigue siendo gratuito y los datos no se muestran públicamente. Estos datos se usan para personalizar el resultado final y guardar el resultado completo en base de datos. Desde allí el usuario ingresa a un flujo tipo wizard de 6 etapas en `/test/paso/{step}`: Realista, Investigativo, Artístico, Social, Emprendedor y Convencional. Cada etapa muestra solo las 6 preguntas de esa dimensión con escala Likert de 1 a 5, valida que todas estén respondidas y avanza al paso siguiente hasta completar las 36 respuestas.

El sistema calcula puntajes reales por dimensión, convierte cada puntaje a porcentaje sobre un máximo de 30 puntos, ordena las dimensiones principales y arma un código vocacional de 3 letras. Además, incluye una base inicial de al menos 40 carreras y oficios en `app/data/careers.py`, cada una con descripción, área, tipo de formación, duración, skills y perfil RIASEC propio.

Las recomendaciones del resultado comparan el perfil RIASEC porcentual del usuario contra el perfil RIASEC de cada carrera, calculan una compatibilidad de 0 a 100 y muestran las mejores opciones ordenadas de mayor a menor compatibilidad.

La pantalla final también incluye un resumen interpretativo del perfil, fortalezas principales, ambientes recomendados donde el estudiante podría rendir mejor y próximos pasos accionables para investigar carreras, comparar planes de estudio y conversar con referentes. Estos textos son orientativos, no clínicos, y acompañan la recomendación de carreras por compatibilidad RIASEC sin reemplazar una evaluación profesional.

Al final de la pantalla de resultado, la sección **Guardar y compartir** permite descargar un informe PDF del resultado con el código vocacional, resumen, scoring RIASEC, dimensiones principales, fortalezas, ambientes recomendados, hasta 6 carreras sugeridas y próximos pasos. El PDF se genera en memoria desde los datos del resultado guardados en la sesión actual y se entrega desde `/resultado/pdf` como archivo descargable; no se guarda en disco. La sesión conserva `last_result_id` para permitir reconstrucciones desde base de datos en una próxima etapa.

Esa misma sección final permite compartir el test por WhatsApp con un enlace hacia `/test`. El enlace usa `PUBLIC_APP_URL` cuando está configurada; si no, se arma desde la URL del request actual. Por ahora no se crea una URL pública única por resultado: se comparte el acceso al test para que otra persona pueda completarlo.

Cuando una persona llega a un resultado real, el navegador guarda en `localStorage` la fecha y hora de finalización (`vocational_test_completed_at`). Si vuelve a entrar a `/test` durante las siguientes 24 horas, se muestra un aviso suave recomendando no repetir el test muchas veces en poco tiempo para mantener la utilidad del resultado. Este aviso no bloquea el acceso, no impide repetir el test y no agrega persistencia en base de datos.

Durante el wizard, las respuestas acumuladas y los datos iniciales opcionales del participante se guardan temporalmente en la sesión HTTP mediante `SessionMiddleware`; al finalizar el test se persisten en base de datos los datos del participante, consentimiento aceptado, respuestas individuales, porcentajes RIASEC, código vocacional, dimensiones principales, carreras recomendadas, insights y fecha de creación; `SESSION_SECRET` puede configurarse por variable de entorno y, si no existe, se usa un valor local de desarrollo. La navegación pública muestra solo el acceso al test y oculta accesos internos o demo como `/resultado/demo` y `/admin`, aunque esas rutas siguen disponibles si se accede directamente.

El footer público incluye enlaces a `/privacidad` y `/aviso-legal` para informar el uso de datos y las aclaraciones principales de la herramienta. La monetización voluntaria se controla con `DONATION_URL`: si se define, el resultado final y el footer muestran enlaces a una página externa de aporte; si se omite, esos elementos no se renderizan y la aplicación funciona igual. No hay integración con API de pagos, checkout interno, pagos obligatorios, guardado de datos de pago, login ni base de datos adicional para esta funcionalidad.

El admin en `/admin` no aparece en la navegación pública y requiere login con `ADMIN_USERNAME` y `ADMIN_PASSWORD`. Muestra métricas básicas desde la base de datos: total de tests completados y últimos 10 resultados con nombre, WhatsApp, código, fecha y situación actual. Desde cada fila permite abrir el detalle completo del resultado guardado, incluyendo datos del participante, consentimiento, scoring RIASEC, top de dimensiones, carreras recomendadas, datos técnicos y respuestas individuales. También permite exportar todos los resultados a CSV desde `/admin/export.csv` para análisis externo. Si las credenciales no están configuradas, el admin muestra un aviso claro y no permite acceder al dashboard.

## Base de datos

La conexión se configura con la variable `DATABASE_URL`. Si no se define, la app usa SQLite local (`sqlite:///./vocacional_dev.db`) para desarrollo. En Render se puede configurar `DATABASE_URL` con PostgreSQL; la app normaliza URLs `postgres://` y `postgresql://` para usar el driver `psycopg` de SQLAlchemy.

En el MVP las tablas se crean automáticamente al iniciar con `Base.metadata.create_all(bind=engine)`. Más adelante se puede migrar a Alembic para manejar cambios de esquema.

## Deploy en Render

El archivo `render.yaml` incluye una configuración inicial para:

- Servicio web Python
- Instalación con `pip install -r requirements.txt`
- Inicio con `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Base de datos PostgreSQL administrada por Render

## Estado actual

Incluye la base funcional inicial, el banco de 36 preguntas RIASEC, el test por etapas desde `/test`, consentimiento obligatorio, persistencia de resultados completos en base de datos, cálculo real de scoring RIASEC, insights interpretativos, recomendación inicial de carreras por compatibilidad RIASEC y login simple para `/admin` mediante variables de entorno, detalle administrativo de resultados y exportación CSV protegida. Todavía no contiene usuarios en base de datos, migraciones Alembic ni machine learning.

### Comentarios y testimonios

Al finalizar el resultado real, las personas pueden dejar un comentario opcional sobre su experiencia con el test. Estos comentarios se guardan en la base de datos como testimonios pendientes (`approved=False`) y no aparecen automáticamente en la landing.

El panel protegido `/admin` muestra un contador de comentarios pendientes y una pantalla en `/admin/testimonios` donde el administrador puede aprobarlos o eliminarlos. Solo los comentarios aprobados por el admin se muestran públicamente en la landing, hasta un máximo de 6 recientes. No se publica el WhatsApp ni datos del test junto con los comentarios.

### Perfil del creador en la landing

`CREATOR_LINKEDIN_URL` permite mostrar un botón hacia el perfil de LinkedIn del creador en la sección pública "Creador del proyecto" de la landing. Es opcional: si se omite o queda vacío, la sección se muestra sin botón. Para evitar enlaces inseguros, el valor debe ser una URL que empiece con `https://`.

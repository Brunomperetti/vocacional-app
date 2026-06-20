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

La ruta `/test` muestra todas las preguntas en una sola pantalla, agrupadas por dimensión y con escala Likert de 1 a 5. El formulario permite responder las 36 preguntas obligatorias, enviar las respuestas con `POST /test` y ver un resultado RIASEC calculado en base a los valores elegidos.

El sistema calcula puntajes reales por dimensión, convierte cada puntaje a porcentaje sobre un máximo de 30 puntos, ordena las dimensiones principales y arma un código vocacional de 3 letras. Además, incluye una base inicial de al menos 40 carreras y oficios en `app/data/careers.py`, cada una con descripción, área, tipo de formación, duración, skills y perfil RIASEC propio.

Las recomendaciones de `/test` comparan el perfil RIASEC porcentual del usuario contra el perfil RIASEC de cada carrera, calculan una compatibilidad de 0 a 100 y muestran las mejores opciones ordenadas de mayor a menor compatibilidad.

En esta etapa las respuestas todavía no se guardan en base de datos y no se crea lógica adicional de persistencia para el test.

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

Incluye la base funcional inicial, el banco de 36 preguntas RIASEC, el formulario completo en `/test`, el cálculo real de scoring RIASEC en memoria y una recomendación inicial de carreras por compatibilidad RIASEC. Todavía no contiene guardado de respuestas del test en base de datos, login real ni machine learning.

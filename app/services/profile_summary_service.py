"""Servicios para generar insights humanos del resultado vocacional."""

DIMENSION_TEXTS: dict[str, dict[str, object]] = {
    "R": {
        "trait": "mirada práctica",
        "summary": "resolver problemas concretos, manipular herramientas, construir, reparar, operar o trabajar con elementos físicos",
        "strengths": ["mirada práctica", "resolución de problemas concretos", "atención al funcionamiento de las cosas"],
        "environments": ["actividades con objetivos claros y problemas concretos", "espacios donde puedas construir, reparar u operar elementos físicos"],
    },
    "I": {
        "trait": "curiosidad analítica",
        "summary": "investigar, comprender, resolver problemas complejos, analizar datos o buscar explicaciones",
        "strengths": ["pensamiento analítico", "curiosidad intelectual", "aprendizaje constante", "resolución de problemas complejos"],
        "environments": ["espacios con autonomía y aprendizaje constante", "proyectos donde haya que investigar y proponer soluciones"],
    },
    "A": {
        "trait": "creatividad expresiva",
        "summary": "imaginar, diseñar, comunicar ideas, crear contenidos o proponer soluciones originales",
        "strengths": ["creatividad aplicada", "comunicación de ideas", "pensamiento original", "sensibilidad estética"],
        "environments": ["entornos creativos o de innovación", "proyectos donde puedas diseñar, comunicar o crear contenidos"],
    },
    "S": {
        "trait": "orientación a las personas",
        "summary": "ayudar, enseñar, acompañar, comunicar, escuchar y trabajar colaborativamente",
        "strengths": ["comunicación", "escucha", "trabajo con personas", "colaboración"],
        "environments": ["equipos donde puedas acompañar, enseñar o comunicar ideas", "contextos colaborativos con contacto frecuente con personas"],
    },
    "E": {
        "trait": "iniciativa para transformar ideas en proyectos",
        "summary": "liderar, persuadir, vender, iniciar proyectos, tomar decisiones y detectar oportunidades",
        "strengths": ["iniciativa", "liderazgo", "toma de decisiones", "persuasión"],
        "environments": ["equipos donde puedas comunicar ideas y coordinar acciones", "proyectos dinámicos con oportunidades para liderar o emprender"],
    },
    "C": {
        "trait": "organización metódica",
        "summary": "ordenar procesos, trabajar con datos, administrar, planificar y gestionar información",
        "strengths": ["organización", "planificación", "atención al detalle", "gestión de información"],
        "environments": ["entornos con procesos claros, datos y planificación", "actividades donde el orden y la precisión sean importantes"],
    },
}

DEFAULT_NEXT_STEPS = [
    "Elegí 3 carreras del ranking y buscá sus planes de estudio.",
    "Mirá videos o entrevistas de profesionales de esas áreas.",
    "Compará duración, salida laboral y materias principales.",
    "Hablá con alguien que estudie o trabaje en una de esas carreras.",
    "Probá una actividad corta relacionada: curso, taller, proyecto o charla.",
    "No tomes la decisión solo por el porcentaje; usalo como punto de partida.",
]


def _dimension_codes(top_dimensions: list) -> list[str]:
    return [str(dimension.get("code", "")).upper() for dimension in top_dimensions if dimension.get("code")]


def _unique(items: list[str], limit: int | None = None) -> list[str]:
    result = list(dict.fromkeys(items))
    return result[:limit] if limit else result


def build_profile_summary(top_dimensions: list, profile_code: str) -> str:
    """Crea un párrafo interpretativo combinando las 3 dimensiones principales."""
    codes = _dimension_codes(top_dimensions)[:3]
    traits = [str(DIMENSION_TEXTS[code]["trait"]) for code in codes if code in DIMENSION_TEXTS]
    activities = [str(DIMENSION_TEXTS[code]["summary"]) for code in codes if code in DIMENSION_TEXTS]

    if not traits:
        return "Tu perfil sugiere intereses variados. Sería recomendable explorar distintas áreas y comparar cuáles conectan mejor con tus motivaciones, habilidades y forma de aprender."

    if len(traits) == 1:
        trait_text = traits[0]
    else:
        trait_text = ", ".join(traits[:-1]) + f" y {traits[-1]}"

    return (
        f"Tu perfil {profile_code} combina {trait_text}. Esto sugiere que podrías sentirte "
        f"cómodo/a en carreras donde puedas {', '.join(activities)}. Estas carreras pueden ser "
        "un buen punto de partida para explorar opciones, no una decisión cerrada."
    )


def build_strengths(top_dimensions: list) -> list[str]:
    """Devuelve fortalezas concretas asociadas a las dimensiones principales."""
    strengths: list[str] = []
    for code in _dimension_codes(top_dimensions):
        strengths.extend(DIMENSION_TEXTS.get(code, {}).get("strengths", []))
    strengths.extend(["aprendizaje constante", "resolución de problemas", "comunicación", "organización"])
    return _unique(strengths, limit=6)


def build_work_environments(top_dimensions: list) -> list[str]:
    """Devuelve ambientes donde el estudiante podría rendir mejor."""
    environments: list[str] = []
    for code in _dimension_codes(top_dimensions):
        environments.extend(DIMENSION_TEXTS.get(code, {}).get("environments", []))
    environments.extend([
        "espacios con autonomía y aprendizaje constante",
        "actividades con objetivos claros y problemas concretos",
        "equipos donde puedas comunicar ideas y coordinar acciones",
    ])
    return _unique(environments, limit=5)


def build_next_steps(recommended_careers: list) -> list[str]:
    """Devuelve acciones recomendadas para profundizar la exploración."""
    steps = DEFAULT_NEXT_STEPS.copy()
    if recommended_careers:
        top_names = [str(career.get("name")) for career in recommended_careers[:3] if career.get("name")]
        if top_names:
            steps.insert(0, f"Revisá con calma estas primeras opciones: {', '.join(top_names)}.")
    return steps[:6]


def build_result_insights(top_dimensions: list, profile_code: str, percentages: dict, recommended_careers: list) -> dict:
    """Agrupa todos los insights interpretativos para el template de resultado."""
    return {
        "profile_summary": build_profile_summary(top_dimensions, profile_code),
        "strengths": build_strengths(top_dimensions),
        "work_environments": build_work_environments(top_dimensions),
        "next_steps": build_next_steps(recommended_careers),
        "percentages": percentages,
    }

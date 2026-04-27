import re
import unicodedata

from sqlmodel import Session, select

from app.core.db import engine
from app.modules.incidents.models import Problem

PROBLEM_ITEMS = [
    {
        "name": "Llanta pinchada",
        "description": "El vehiculo presenta pinchazo o perdida de aire en una llanta.",
    },
    {
        "name": "Bateria descargada",
        "description": "El vehiculo no enciende por falta de carga en la bateria.",
    },
    {
        "name": "Falla de alternador",
        "description": "La bateria no mantiene carga por posible falla del alternador.",
    },
    {
        "name": "Falla de motor de arranque",
        "description": "El vehiculo no arranca por problemas en el sistema de arranque.",
    },
    {
        "name": "Sin combustible",
        "description": "El vehiculo se quedo detenido por falta de combustible.",
    },
    {
        "name": "Llaves dentro del vehiculo",
        "description": "El usuario no puede ingresar al vehiculo por bloqueo de puertas.",
    },
    {
        "name": "Falla en frenos",
        "description": "Se detecta perdida de frenado o ruido severo en el sistema de frenos.",
    },
    {
        "name": "Sobrecalentamiento de motor",
        "description": "La temperatura del motor supera limites seguros de operacion.",
    },
    {
        "name": "Problema de suspension",
        "description": "El vehiculo presenta golpes, desnivel o inestabilidad en suspension.",
    },
    {
        "name": "Mantenimiento urgente de aceite",
        "description": "El vehiculo requiere cambio de aceite de forma inmediata.",
    },
    {
        "name": "Luz check engine encendida",
        "description": "Se requiere escaneo de codigos de falla por luz de motor encendida.",
    },
    {
        "name": "Vehiculo no enciende",
        "description": "El vehiculo no enciende y requiere diagnostico rapido en ruta.",
    },
    {
        "name": "Averia mecanica en ruta",
        "description": "El vehiculo presenta una averia general y necesita asistencia inmediata.",
    },
]


def make_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    lowered = ascii_text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", lowered)
    collapsed = re.sub(r"[\s_-]+", "-", cleaned)
    return collapsed.strip("-")


def seed_problems(db: Session) -> dict[str, int]:
    created = 0

    for item in PROBLEM_ITEMS:
        slug = make_slug(item["name"])
        existing = db.exec(
            select(Problem).where(Problem.slug == slug, Problem.state == True)
        ).first()
        if existing:
            continue

        db.add(
            Problem(
                name=item["name"],
                slug=slug,
                description=item["description"],
            )
        )
        created += 1

    db.commit()

    total = len(db.exec(select(Problem).where(Problem.state == True)).all())
    return {
        "created": created,
        "total_available": total,
    }


def run_seed() -> None:
    with Session(engine) as db:
        result = seed_problems(db)
        print(
            "Problems seed completed | created="
            f"{result['created']} total_available={result['total_available']}"
        )


if __name__ == "__main__":
    run_seed()

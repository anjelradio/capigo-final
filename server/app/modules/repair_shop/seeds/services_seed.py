import re
import unicodedata
from sqlmodel import Session

from app.core.db import engine
from app.modules.repair_shop.models import Service
from app.modules.repair_shop.repositories import ServiceRepository

SERVICE_NAMES = [
    "Parche de llanta",
    "Cambio de llanta",
    "Auxilio por pinchazo",
    "Recarga de bateria",
    "Cambio de bateria",
    "Paso de corriente",
    "Diagnostico electrico basico",
    "Reparacion de alternador",
    "Reparacion de arranque",
    "Suministro de combustible",
    "Apertura de vehiculo",
    "Remolque con grua",
    "Reparacion de frenos",
    "Cambio de pastillas de freno",
    "Reparacion de radiador",
    "Atencion por sobrecalentamiento",
    "Cambio de aceite de emergencia",
    "Escaneo OBD basico",
    "Revision de suspension",
    "Asistencia mecanica en ruta",
]


def make_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    lowered = ascii_text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", lowered)
    collapsed = re.sub(r"[\s_-]+", "-", cleaned)
    return collapsed.strip("-")


def seed_services(db: Session) -> dict[str, int]:
    repository = ServiceRepository(db)
    created = 0

    for name in SERVICE_NAMES:
        slug = make_slug(name)
        existing = repository.get_by_slug(slug)
        if existing:
            continue

        repository.create(Service(name=name, slug=slug))
        created += 1

    db.commit()
    total = len(repository.list_available())
    return {
        "created": created,
        "total_available": total,
    }


def run_seed() -> None:
    with Session(engine) as db:
        result = seed_services(db)
        print(
            "Services seed completed | created="
            f"{result['created']} total_available={result['total_available']}"
        )


if __name__ == "__main__":
    run_seed()

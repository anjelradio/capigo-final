from sqlmodel import Session, select

from app.core.db import engine
from app.modules.incidents.models import Problem, ProblemServiceMap
from app.modules.incidents.seeds.problem_seed import seed_problems
from app.modules.repair_shop.models import Service

PROBLEM_SERVICE_SLUGS = {
    "llanta-pinchada": [
        "parche-de-llanta",
        "cambio-de-llanta",
        "auxilio-por-pinchazo",
        "asistencia-mecanica-en-ruta",
    ],
    "bateria-descargada": [
        "recarga-de-bateria",
        "cambio-de-bateria",
        "paso-de-corriente",
        "diagnostico-electrico-basico",
    ],
    "falla-de-alternador": [
        "diagnostico-electrico-basico",
        "reparacion-de-alternador",
        "paso-de-corriente",
        "remolque-con-grua",
    ],
    "falla-de-motor-de-arranque": [
        "diagnostico-electrico-basico",
        "reparacion-de-arranque",
        "paso-de-corriente",
        "remolque-con-grua",
    ],
    "sin-combustible": [
        "suministro-de-combustible",
        "asistencia-mecanica-en-ruta",
    ],
    "llaves-dentro-del-vehiculo": [
        "apertura-de-vehiculo",
        "asistencia-mecanica-en-ruta",
    ],
    "falla-en-frenos": [
        "reparacion-de-frenos",
        "cambio-de-pastillas-de-freno",
        "remolque-con-grua",
    ],
    "sobrecalentamiento-de-motor": [
        "atencion-por-sobrecalentamiento",
        "reparacion-de-radiador",
        "remolque-con-grua",
    ],
    "problema-de-suspension": [
        "revision-de-suspension",
        "asistencia-mecanica-en-ruta",
        "remolque-con-grua",
    ],
    "mantenimiento-urgente-de-aceite": [
        "cambio-de-aceite-de-emergencia",
        "asistencia-mecanica-en-ruta",
    ],
    "luz-check-engine-encendida": [
        "escaneo-obd-basico",
        "diagnostico-electrico-basico",
        "asistencia-mecanica-en-ruta",
    ],
    "vehiculo-no-enciende": [
        "paso-de-corriente",
        "cambio-de-bateria",
        "reparacion-de-arranque",
        "diagnostico-electrico-basico",
        "remolque-con-grua",
    ],
    "averia-mecanica-en-ruta": [
        "asistencia-mecanica-en-ruta",
        "escaneo-obd-basico",
        "remolque-con-grua",
    ],
}


def _get_active_problem_by_slug(db: Session, slug: str) -> Problem | None:
    return db.exec(
        select(Problem).where(Problem.slug == slug, Problem.state == True)
    ).first()


def _get_active_service_by_slug(db: Session, slug: str) -> Service | None:
    return db.exec(
        select(Service).where(
            Service.slug == slug,
            Service.state == True,
            Service.is_available == True,
        )
    ).first()


def seed_problem_service_map(db: Session) -> dict[str, int]:
    seed_problems(db)

    created = 0
    missing_problems: list[str] = []
    missing_services: list[str] = []

    for problem_slug, service_slugs in PROBLEM_SERVICE_SLUGS.items():
        problem = _get_active_problem_by_slug(db, problem_slug)
        if not problem:
            missing_problems.append(problem_slug)
            continue

        for service_slug in service_slugs:
            service = _get_active_service_by_slug(db, service_slug)
            if not service:
                missing_services.append(service_slug)
                continue

            existing = db.exec(
                select(ProblemServiceMap).where(
                    ProblemServiceMap.problem_id == problem.id,
                    ProblemServiceMap.service_id == service.id,
                    ProblemServiceMap.state == True,
                )
            ).first()
            if existing:
                continue

            db.add(
                ProblemServiceMap(
                    problem_id=problem.id,
                    service_id=service.id,
                )
            )
            created += 1

    if missing_problems or missing_services:
        missing_problems = sorted(set(missing_problems))
        missing_services = sorted(set(missing_services))
        detail = []
        if missing_problems:
            detail.append(f"problems={','.join(missing_problems)}")
        if missing_services:
            detail.append(f"services={','.join(missing_services)}")
        raise ValueError("No se pudo completar problem_service_map seed: " + " | ".join(detail))

    db.commit()

    total = len(db.exec(select(ProblemServiceMap).where(ProblemServiceMap.state == True)).all())
    return {
        "created": created,
        "total_available": total,
    }


def run_seed() -> None:
    with Session(engine) as db:
        result = seed_problem_service_map(db)
        print(
            "Problem service map seed completed | created="
            f"{result['created']} total_available={result['total_available']}"
        )


if __name__ == "__main__":
    run_seed()

from sqlmodel import SQLModel, Session, select

from app.core.db import engine
from app.modules.user.models import VehicleType, VehicleTypeName

VEHICLE_TYPES = [
    VehicleTypeName.CAR,
    VehicleTypeName.MOTORCYCLE,
    VehicleTypeName.TRUCK,
]


def seed_vehicle_types(db: Session) -> dict[str, int]:
    created = 0

    for vehicle_type in VEHICLE_TYPES:
        existing = db.exec(
            select(VehicleType).where(
                VehicleType.name == vehicle_type,
                VehicleType.state == True,
            )
        ).first()

        if existing:
            continue

        db.add(VehicleType(name=vehicle_type))
        created += 1

    db.commit()

    total = len(
        db.exec(select(VehicleType).where(VehicleType.state == True)).all()
    )

    return {
        "created": created,
        "total_available": total,
    }


def run_seed() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as db:
        result = seed_vehicle_types(db)
        print(
            "Vehicle types seed completed | created="
            f"{result['created']} total_available={result['total_available']}"
        )


if __name__ == "__main__":
    run_seed()

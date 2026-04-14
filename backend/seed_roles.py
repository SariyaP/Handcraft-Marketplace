from app.database import SessionLocal, init_db
from app.services.auth import ensure_system_roles


def seed_roles() -> None:
    init_db()

    with SessionLocal() as session:
        ensure_system_roles(session)


if __name__ == "__main__":
    seed_roles()

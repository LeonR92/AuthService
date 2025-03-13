from core.database import Base, write_engine


def init_db():
    """Ensures all models are registered before creating tables."""
    Base.metadata.create_all(write_engine)

if __name__ == "__main__":
    init_db()

from core.database import Base, write_engine
# Import models to register them
#from blueprints.users import models as user_models

def init_db():
    """Ensures all models are registered before creating tables."""
    Base.metadata.create_all(write_engine)

if __name__ == "__main__":
    init_db()

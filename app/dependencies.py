from app.database import engine
from sqlalchemy.orm import Session

def get_db():
    with Session(engine) as session:
        yield session

        

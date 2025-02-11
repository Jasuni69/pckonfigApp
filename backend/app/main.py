from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import CPU

app = FastAPI()

@app.get("/cpus")
def get_cpus(db: Session = Depends(get_db)):
    return db.query(CPU).all()

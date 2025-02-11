import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Setup SQLAlchemy
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
session = SessionLocal()

Base = declarative_base()

# Define CPU Cooler Table Model
class CPUCooler(Base):
    __tablename__ = 'cpu_coolers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    type = Column(String, nullable=False)  # AIO or Air
    color = Column(String)
    size = Column(Integer)  # Radiator size (AIO) or Fan size (Air)
    price = Column(DECIMAL(10,2), nullable=False)

# Function to insert CPU coolers from JSON
def insert_from_json(json_file):
    try:
        with open(json_file, 'r', encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found - {json_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file}")
        return

    new_records = 0
    for item in data:
        # Check if cooler already exists (by name)
        existing_cooler = session.query(CPUCooler).filter_by(name=item["name"]).first()
        if existing_cooler:
            print(f"Skipping duplicate: {item['name']}")
            continue

        # Convert price safely
        try:
            price = float(item["price"]) if isinstance(item["price"], (int, float)) else float(item["price"].replace(",", "").replace("kr", "").strip())
        except ValueError:
            print(f"Error: Invalid price format for {item['name']}")
            continue

        # Ensure values exist, otherwise set defaults
        cooler = CPUCooler(
            name=item["name"],
            brand=item["brand"],
            type=item.get("type", "Unknown"),
            color=item.get("color", "Unknown"),
            size=int(item["size"]) if item.get("size") is not None else None,
            price=price
        )
        session.add(cooler)
        new_records += 1

    session.commit()
    print(f"Inserted {new_records} new records from {json_file} successfully.")

# Run the function
if __name__ == "__main__":
         insert_from_json("../../scraping/cleaned data/coolers.json")  # Path to Intel CPUs JSON

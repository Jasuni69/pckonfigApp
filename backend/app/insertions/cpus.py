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

# Define CPU Table Model
class CPU(Base):
    __tablename__ = 'cpus'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    socket = Column(String)
    cores = Column(Integer, nullable=False)
    threads = Column(Integer)
    base_clock = Column(DECIMAL(5,2))
    cache = Column(Integer)
    price = Column(DECIMAL(10,2), nullable=False)

# Function to insert CPUs from JSON
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
        # Check if CPU already exists (by name)
        existing_cpu = session.query(CPU).filter_by(name=item["name"]).first()
        if existing_cpu:
            print(f"Skipping duplicate: {item['name']}")
            continue

        # Convert price safely
        try:
            price = float(item["price"]) if isinstance(item["price"], (int, float)) else float(item["price"].replace(",", "").replace("kr", "").strip())
        except ValueError:
            print(f"Error: Invalid price format for {item['name']}")
            continue

        # Ensure values exist, otherwise set defaults
        cpu = CPU(
            name=item["name"],
            brand=item["brand"],
            socket=item.get("socket", "Unknown"),
            cores=int(item["cores"]) if item.get("cores") is not None else 0,  # Default to 0 if missing
            threads=int(item["threads"]) if item.get("threads") is not None else None,
            base_clock=float(item["base_clock"]) if item.get("base_clock") is not None else None,
            cache=int(item["cache"]) if item.get("cache") is not None else None,
            price=price
        )
        session.add(cpu)
        new_records += 1

    session.commit()
    print(f"Inserted {new_records} new records from {json_file} successfully.")

# Run the function for both Intel & AMD CPUs
if __name__ == "__main__":
    insert_from_json("../../scraping/cleaned data/intel-cpu.json")  # Path to Intel CPUs JSON
    insert_from_json("../../scraping/cleaned data/amd-cpu.json")  # Path to AMD CPUs JSON

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

# Define GPU Table Model
class GPU(Base):
    __tablename__ = 'gpus'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    memory = Column(String, nullable=False)
    interface = Column(String, nullable=False)
    base_clock = Column(DECIMAL(8,2))
    price = Column(DECIMAL(10,2), nullable=False)
    recommended_wattage = Column(DECIMAL(8,2))

# Function to insert GPUs from JSON
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
        # Check if GPU already exists (by name)
        existing_gpu = session.query(GPU).filter_by(name=item["name"]).first()
        if existing_gpu:
            print(f"Skipping duplicate: {item['name']}")
            continue

        # Convert price safely
        try:
            price = float(str(item["price"]).replace(",", "").replace("kr", "").strip())
        except ValueError:
            print(f"Error: Invalid price format for {item['name']}")
            continue

        # Ensure values exist, otherwise set defaults
        gpu = GPU(
            name=item["name"],
            brand=item["brand"],
            model=item["model"],
            memory=item["memory"],
            interface=item["interface"],
            base_clock=float(item["base_clock"]) if item.get("base_clock") is not None else None,
            price=price,
            recommended_wattage=float(item["recommended_wattage"]) if item.get("recommended_wattage") is not None else None
        )
        session.add(gpu)
        new_records += 1

    session.commit()
    print(f"Inserted {new_records} new records from {json_file} successfully.")

# Run the function for both AMD & NVIDIA GPUs
if __name__ == "__main__":
    insert_from_json("../../scraping/cleaned data/amd-gpu-updated.json")  # AMD GPUs
    insert_from_json("../../scraping/cleaned data/nvidia-gpu-updated.json")  # NVIDIA GPUs

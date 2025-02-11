import json
import os
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Set up SQLAlchemy connection
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
Base = declarative_base()

# Define Motherboard Table
class Motherboard(Base):
    __tablename__ = 'motherboards'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    socket = Column(String, nullable=False)
    form_factor = Column(String, nullable=False)
    chipset = Column(String, nullable=False)
    memory_type = Column(String, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

# Function to insert JSON data
def insert_from_json(json_file):
    try:
        with open(json_file, 'r', encoding="utf-8") as f:
            data = json.load(f)

        inserted_count = 0

        for item in data:
            # Check if the motherboard already exists
            exists = session.query(Motherboard).filter_by(name=item["name"]).first()
            if exists:
                print(f"Skipping duplicate: {item['name']}")
                continue

            # Insert new motherboard record
            motherboard = Motherboard(
                name=item["name"],
                brand=item["brand"],
                socket=item["socket"],
                form_factor=item["form_factor"],
                chipset=item["chipset"],
                memory_type=item["memory_type"],
                price=float(item["price"]) if item["price"] is not None else 0.0
            )
            session.add(motherboard)
            inserted_count += 1

        session.commit()
        print(f"Inserted {inserted_count} new records from {json_file} successfully.")

    except Exception as e:
        print(f"Error inserting data from {json_file}: {e}")

# Run the script for AMD and Intel motherboards
if __name__ == "__main__":
    insert_from_json("../../scraping/cleaned data/amd-mb.json")  # AMD motherboards
    insert_from_json("../../scraping/cleaned data/intel-mb.json")  # Intel motherboards

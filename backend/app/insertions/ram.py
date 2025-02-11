import json
import os
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# SQLAlchemy Setup
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
Base = declarative_base()

# Define RAM Table Model
class RAM(Base):
    __tablename__ = 'ram'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    type = Column(String)
    latency = Column(String)
    capacity = Column(DECIMAL(6,2))
    speed = Column(DECIMAL(6,2))
    memory_type = Column(String)
    price = Column(DECIMAL(10,2))

# JSON File Path
json_file = os.path.abspath("../../scraping/cleaned data/ram.json")
print(f"Loading JSON file from: {json_file}")

# Check if the file exists
if not os.path.exists(json_file):
    print(f"Error: JSON file not found at {json_file}!")
    exit()

# Insert JSON Data
def insert_from_json(json_file):
    try:
        with open(json_file, 'r', encoding="utf-8") as f:
            data = json.load(f)

        inserted_count = 0
        for item in data:
            # Check for duplicates
            exists = session.query(RAM).filter_by(name=item["name"]).first()
            if exists:
                print(f"Skipping duplicate: {item['name']}")
                continue

            # Insert RAM record
            ram = RAM(
                name=item["name"],
                brand=item.get("brand"),
                type=item.get("type"),
                latency=item.get("latency"),
                capacity=float(item["capacity"]) if item.get("capacity") is not None else None,
                speed=float(item["speed"]) if item.get("speed") is not None else None,
                memory_type=item.get("memory_type"),
                price=float(item["price"]) if item.get("price") is not None else None
            )
            session.add(ram)
            inserted_count += 1

        session.commit()
        print(f"Inserted {inserted_count} new records from {json_file} successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")

# Run the insertion
if __name__ == "__main__":
    insert_from_json(json_file)

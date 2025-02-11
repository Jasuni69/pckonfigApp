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

# Define PSU Table
class PSU(Base):
    __tablename__ = 'psus'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    wattage = Column(Integer, nullable=False)
    efficiency = Column(String, nullable=False)
    size = Column(DECIMAL(5,2))  # Adjust precision if needed
    color = Column(String)
    price = Column(DECIMAL(10,2), nullable=False)

# Path to JSON file
json_file = os.path.abspath("../../scraping/cleaned data/psus.json")
print(f"Loading JSON file from: {json_file}")

# Check if JSON file exists
if not os.path.exists(json_file):
    print(f"Error: JSON file not found at {json_file}!")
    exit()

# Insert JSON data
def insert_from_json(json_file):
    try:
        with open(json_file, 'r', encoding="utf-8") as f:
            data = json.load(f)

        inserted_count = 0
        for item in data:
            # Check for duplicates
            exists = session.query(PSU).filter_by(name=item["name"]).first()
            if exists:
                print(f"Skipping duplicate: {item['name']}")
                continue

            # Insert PSU record
            psu = PSU(
                name=item["name"],
                brand=item["brand"],
                wattage=int(item["wattage"]),
                efficiency=item["efficiency"],
                size=float(item["size"]) if item["size"] is not None else None,
                color=item["color"],
                price=float(item["price"]) if item["price"] is not None else 0.0
            )
            session.add(psu)
            inserted_count += 1

        session.commit()
        print(f"Inserted {inserted_count} new records from {json_file} successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")

# Run the insertion
if __name__ == "__main__":
    insert_from_json(json_file)

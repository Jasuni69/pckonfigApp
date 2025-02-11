import json
import os
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Text
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

# Define Chassis Table Model
class Chassis(Base):
    __tablename__ = 'chassis'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    form_factor = Column(String)
    power_supply = Column(String)
    color = Column(String)
    additional_features = Column(Text)  # Allows for long text descriptions
    price = Column(DECIMAL(10,2))

# JSON File Path
json_file = os.path.abspath("../../scraping/cleaned data/chassis.json")
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
            exists = session.query(Chassis).filter_by(name=item["name"]).first()
            if exists:
                print(f"Skipping duplicate: {item['name']}")
                continue

            # Insert Chassis record
            chassis = Chassis(
                name=item["name"],
                brand=item.get("brand"),
                form_factor=item.get("form_factor"),
                power_supply=item.get("power_supply"),
                color=item.get("color"),
                additional_features=item.get("additional_features"),
                price=float(item["price"]) if item.get("price") is not None else None
            )
            session.add(chassis)
            inserted_count += 1

        session.commit()
        print(f"Inserted {inserted_count} new records from {json_file} successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")

# Run the insertion
if __name__ == "__main__":
    insert_from_json(json_file)

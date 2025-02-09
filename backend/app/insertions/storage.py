import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DB_URL = os.getenv("DB_URL")

# Set up SQLAlchemy
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base = declarative_base()

# Define the storage_devices table
class StorageDevice(Base):
    __tablename__ = 'storage_devices'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    type = Column(String, nullable=False)
    form_factor = Column(String)
    capacity = Column(DECIMAL(6,2), nullable=False)
    interface = Column(String)
    rpm = Column(Integer)
    read_speed = Column(DECIMAL(6,2))
    write_speed = Column(DECIMAL(6,2))
    price = Column(DECIMAL(10,2), nullable=False)

# Function to insert JSON data
def insert_from_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    for item in data:
        device = StorageDevice(
            name=item.get("name"),
            brand=item.get("brand"),
            type=item.get("type"),
            form_factor=item.get("form_factor"),
            capacity=float(item.get("capacity", 0)),
            interface=item.get("interface"),
            rpm=item.get("rpm"),
            read_speed=item.get("read_speed"),
            write_speed=item.get("write_speed"),
            price=float(item.get("price", 0))
        )
        session.add(device)

    session.commit()
    print(f"Inserted {len(data)} records successfully.")

# Run the function
if __name__ == "__main__":
    insert_from_json("storage_data.json")

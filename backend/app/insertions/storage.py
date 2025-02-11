import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DB_URL = os.getenv("DB_URL")

# Set up SQLAlchemy
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base = declarative_base()

# Define the storage_devices table with increased precision for high values
class StorageDevice(Base):
    __tablename__ = 'storage_devices'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    type = Column(String, nullable=False)
    form_factor = Column(String)
    capacity = Column(DECIMAL(10, 2), nullable=False)  # ✅ Increased precision for large TB values
    interface = Column(String)
    rpm = Column(Integer)
    read_speed = Column(DECIMAL(10, 2))  # ✅ Increased precision for high-speed SSDs
    write_speed = Column(DECIMAL(10, 2))  # ✅ Increased precision for write speeds
    price = Column(DECIMAL(10, 2), nullable=False)  # ✅ Increased to handle large prices

    __table_args__ = (
        CheckConstraint("type IN ('HDD', 'SSD')", name="storage_devices_type_check"),
    )

# Function to extract numerical capacity (in GB) from strings like '500 GB' or '2 TB'
def extract_capacity(value):
    """Convert storage capacity from strings like '500 GB' or '2 TB' to a float in GB."""
    if isinstance(value, str):
        value = value.upper().replace("GB", "").replace("TB", "").strip()
        try:
            return float(value) * (1000 if "TB" in value else 1)  # Convert TB to GB
        except ValueError:
            return 0.0  # Default if conversion fails
    return float(value)

# Function to determine if an item is an HDD or SSD
def determine_type(item):
    """Infer the type (HDD or SSD) based on available data."""
    interface = item.get("interface", "").lower() if item.get("interface") else ""  # Ensure it's a string
    form_factor = item.get("form_factor", "").lower() if item.get("form_factor") else ""  # Ensure it's a string

    if "rpm" in item and item["rpm"]:  # If RPM exists, it's an HDD
        return "HDD"
    elif "nvme" in interface:  # If NVMe is found in the interface string, it's an SSD
        return "SSD"
    elif "m.2" in form_factor:  # If M.2 form factor, likely an SSD
        return "SSD"
    else:
        return "HDD"  # Default to HDD if unsure

# Function to insert JSON data into the database
def insert_from_json(json_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        inserted_count = 0
        for item in data:
            item_type = determine_type(item)  # Ensure correct type (HDD or SSD)

            # Check if a record with the same name already exists
            existing_device = session.query(StorageDevice).filter_by(name=item.get("name")).first()

            if not existing_device:
                device = StorageDevice(
                    name=item.get("name"),
                    brand=item.get("brand"),
                    type=item_type,  # ✅ Ensure correct type
                    form_factor=item.get("form_factor"),
                    capacity=extract_capacity(item.get("capacity", 0)),
                    interface=item.get("interface"),
                    rpm=item.get("rpm"),
                    read_speed=item.get("read_speed"),
                    write_speed=item.get("write_speed"),
                    price=float(item.get("price", 0))
                )
                session.add(device)
                inserted_count += 1
            else:
                print(f"Skipping duplicate: {item.get('name')}")

        session.commit()
        print(f"Inserted {inserted_count} new records from {json_file} successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error inserting data from {json_file}: {e}")

# Ensure the database table exists before inserting data
if __name__ == "__main__":
    Base.metadata.create_all(engine)  # ✅ Ensures the table exists before inserting

    json_files = [
        "../../scraping/cleaned data/ssd.json",
        "../../scraping/cleaned data/3.5-hdd.json"
    ]

    for file in json_files:
        insert_from_json(file)

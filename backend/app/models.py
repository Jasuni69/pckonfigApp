from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CPU(Base):
    __tablename__ = "cpus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    socket = Column(String)
    cores = Column(Integer, nullable=False)
    threads = Column(Integer)
    base_clock = Column(Float)
    cache = Column(Integer)
    price = Column(Float, nullable=False)

class RAM(Base):
    __tablename__ = "ram"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    type = Column(String)
    latency = Column(String)
    capacity = Column(Float)
    speed = Column(Float)
    memory_type = Column(String)
    price = Column(Float)

class PSU(Base):
    __tablename__ = "psus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    wattage = Column(Integer)
    efficiency = Column(String)
    size = Column(Float)
    color = Column(String)
    price = Column(Float)

class GPU(Base):
    __tablename__ = "gpus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    model = Column(String)
    memory = Column(String)
    interface = Column(String)
    base_clock = Column(Float, nullable=True)
    recommended_wattage = Column(Float)
    price = Column(Float)

class Case(Base):
    __tablename__ = "chassis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    form_factor = Column(String)
    power_supply = Column(String)
    color = Column(String)
    additional_features = Column(String, nullable=True)
    price = Column(Float)

class Motherboard(Base):
    __tablename__ = "motherboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    socket = Column(String)
    form_factor = Column(String)
    chipset = Column(String)
    memory_type = Column(String)
    price = Column(Float)

class Storage(Base):
    __tablename__ = "storage_devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    form_factor = Column(String)
    capacity = Column(Float)
    interface = Column(String)
    rpm = Column(Float, nullable=True)
    read_speed = Column(Float, nullable=True)
    write_speed = Column(Float, nullable=True)
    price = Column(Float)

class Cooler(Base):
    __tablename__ = "cpu_coolers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    type = Column(String)
    color = Column(String)
    size = Column(Float, nullable=True)
    price = Column(Float)

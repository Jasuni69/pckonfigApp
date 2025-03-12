from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

class Token(Base):
    __tablename__ = "tokens"

    created: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="tokens")

class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    tokens: Mapped[list["Token"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email}>"

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
    recommended_wattage = Column(Float, nullable=True)
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

class SavedBuild(Base):
    __tablename__ = "saved_builds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cpu_id = Column(Integer, ForeignKey("cpus.id"))
    gpu_id = Column(Integer, ForeignKey("gpus.id"))
    motherboard_id = Column(Integer, ForeignKey("motherboards.id"))
    ram_id = Column(Integer, ForeignKey("ram.id"))
    psu_id = Column(Integer, ForeignKey("psus.id"))
    case_id = Column(Integer, ForeignKey("chassis.id"))
    storage_id = Column(Integer, ForeignKey("storage_devices.id"))
    cooler_id = Column(Integer, ForeignKey("cpu_coolers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="saved_builds")
    cpu = relationship("CPU")
    gpu = relationship("GPU")
    motherboard = relationship("Motherboard")
    ram = relationship("RAM")
    psu = relationship("PSU")
    case = relationship("Case")
    storage = relationship("Storage")
    cooler = relationship("Cooler")
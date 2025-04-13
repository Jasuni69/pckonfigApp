class SavedBuild(Base):
    __tablename__ = "saved_builds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    purpose = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cpu_id = Column(Integer, ForeignKey("cpus.id"))
    gpu_id = Column(Integer, ForeignKey("gpus.id"))
    motherboard_id = Column(Integer, ForeignKey("motherboards.id"))
    ram_id = Column(Integer, ForeignKey("ram.id"))
    psu_id = Column(Integer, ForeignKey("psus.id"))
    case_id = Column(Integer, ForeignKey("chassis.id"))
    storage_id = Column(Integer, ForeignKey("storage_devices.id"))
    cooler_id = Column(Integer, ForeignKey("cpu_coolers.id"))
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = Column(Boolean, default=False) 
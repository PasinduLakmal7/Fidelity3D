import enum
from sqlalchemy import Column, Integer, String, Enum
from shared.database import Base

class JobStatus(enum.Enum):
    FREE_PENDING = "FREE_PENDING"
    FREE_PROCESSING = "FREE_PROCESSING"
    FREE_COMPLETED = "FREE_COMPLETED"
    PAID_PENDING = "PAID_PENDING"
    PAID_PROCESSING = "PAID_PROCESSING"
    PAID_COMPLETED = "PAID_COMPLETED"
    FAILED = "FAILED"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.FREE_PENDING, nullable=False)
    image_paths = Column(String, nullable=False)
    output_file_path = Column(String, nullable=True)

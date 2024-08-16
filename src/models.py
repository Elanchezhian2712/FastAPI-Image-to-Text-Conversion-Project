from sqlalchemy import Column, Integer, String, Date
from src.database import Base

class CandidateData(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    govt_rank = Column(String, index=True)
    application_number = Column(String, index=True)
    name = Column(String, index=True)
    dob = Column(Date)
    aggregate_mark = Column(String)
    community = Column(String)
    govt_community_rank = Column(String)
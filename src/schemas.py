from pydantic import BaseModel
from datetime import date

class CandidateDataSchema(BaseModel):
    govt_rank: str
    application_number: str
    name: str
    dob: date
    aggregate_mark: str
    community: str
    govt_community_rank: str

    class Config:
        orm_mode = True

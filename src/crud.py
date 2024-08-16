from sqlalchemy.orm import Session
from src.models import CandidateData
from datetime import date

def create_candidate_data(
    db: Session,
    govt_rank: str,
    application_number: str,
    name: str,
    dob: date,
    aggregate_mark: str,
    community: str,
    govt_community_rank: str
):
    try:
        new_data = CandidateData(
            govt_rank=govt_rank,
            application_number=application_number,
            name=name,
            dob=dob,
            aggregate_mark=aggregate_mark,
            community=community,
            govt_community_rank=govt_community_rank
        )

        db.add(new_data)
        db.commit()
        db.refresh(new_data)  # Refresh instance with updated data from DB
        return new_data
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise e  # Re-raise the exception to handle it in main.py

from typing import Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime

class JobModel(BaseModel):
    job_id: str
    job_title: str
    job_city: Optional[str]
    job_state: Optional[str]
    job_link: HttpUrl
    job_description: str
    job_types: list[str]
    published_date: datetime

    salary_max: Optional[float]
    salary_min: Optional[float]
    salary_type: Optional[str]
    salary_currency: Optional[str]

    employer_name: str
    employer_rating: float
    employer_review_count: int
    
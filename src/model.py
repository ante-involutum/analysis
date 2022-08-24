from pydantic import BaseModel


class Job(BaseModel):
    job_type: str
    job_name: str
    from_: int
    size: int

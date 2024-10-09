from typing import Optional

from pydantic import BaseModel, ConfigDict

########################################################################################


class UserRegistrationForm(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    user_id: str
    username: str


class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    task: str
    backend: str
    status: str
    result: Optional[str] = None
    user_id: str

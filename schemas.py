from pydantic import BaseModel
from typing import List

class UserRequest(BaseModel):
    username: str
    email: str
    password: str

class TaskRequest(BaseModel):
    title: str
    description: str
    due_date: str
    completed: bool

class TaskAssignmentRequest(BaseModel):
    task_id: int
    user_id: int
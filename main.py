from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

SQLALCHEMY_DATABASE_URL = 'sqlite:///todo.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    tasks = relationship('TaskAssignment', back_populates='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(Date)
    completed = Column(Boolean, default=False)
    task_assignments = relationship('TaskAssignment', back_populates='task')

class TaskAssignment(Base):
    __tablename__ = 'task_assignments'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task = relationship('Task', back_populates='task_assignments')
    user = relationship('User', back_populates='tasks')

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

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

@app.post('/users/')
async def create_user(user: UserRequest):
    db_user = User(username=user.username, email=user.email)
    db_user.set_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get('/users/')
async def read_users():
    return db.query(User).all()

@app.post('/tasks/')
async def create_task(task: TaskRequest):
    db_task = Task(title=task.title, description=task.description, due_date=task.due_date, completed=task.completed)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get('/tasks/')
async def read_tasks():
    return db.query(Task).all()

@app.post('/task_assignments/')
async def create_task_assignment(task_assignment: TaskAssignmentRequest):
    db_task_assignment = TaskAssignment(task_id=task_assignment.task_id, user_id=task_assignment.user_id)
    db.add(db_task_assignment)
    db.commit()
    db.refresh(db_task_assignment)
    return db_task_assignment

@app.get('/task_assignments/')
async def read_task_assignments():
    return db.query(TaskAssignment).all()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
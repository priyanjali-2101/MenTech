from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# ── Feature 1: CREATE item ──────────────────────
@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


# ── Feature 2: GET ALL items ────────────────────
@app.get("/todos", response_model=List[schemas.TodoResponse])
def get_all_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()


# ── Feature 3: GET SINGLE item ──────────────────
@app.get("/todos/{id}", response_model=schemas.TodoResponse)
def get_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


# ── Feature 4: UPDATE item ──────────────────────
@app.put("/todos/{id}", response_model=schemas.TodoResponse)
def update_todo(id: int, data: schemas.TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


# ── Feature 5: DELETE item ──────────────────────
@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import Column, Integer, String, ARRAY



app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        v = validate_email(user.email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Invalid email")

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=schemas.User)
def patch_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.name is None or user.email is None:
        raise HTTPException(status_code=400, detail="Name and Email are required")

    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.get("/match/{user_id}", response_model=list[int])
def match_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    interests = set(user.interests.split(","))
    curr_gender = user.gender

    matching_user_ids = []

    all_users = db.query(models.User).all()

    for u in all_users:
        match_interests = set(u.interests.split(","))
        match_gender = u.gender

        if interests.intersection(match_interests) and curr_gender != match_gender:
            matching_user_ids.append(u.id)

    return matching_user_ids


@app.get("/check-emails")
def check_emails(db:Session = Depends(get_db)):
    all_users = db.query(models.User).all()
    
    for u in all_users:
        try:
            v = validate_email(u.email)
        except EmailNotValidError as e:
            return {"message": "Some emails are Invalid"}
    
    return {"message": "All emails are valid"}

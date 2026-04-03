from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api import auth
from app.api import teams

app = FastAPI(title="Business Management System")
app.include_router(auth.router)
app.include_router(teams.router)


@app.post("/users/")
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    user = User(email=email, hashed_password=password, full_name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

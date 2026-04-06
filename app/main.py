from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db, engine
from app.models.user import User
from app.api import auth
from app.api import teams
from app.api import task
from app.api import meetings
from app.api import calendar
from app.api import evaluations
from app.admin import setup_admin

app = FastAPI(title="Business Management System")

app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(task.router)
app.include_router(meetings.router)
app.include_router(calendar.router)
app.include_router(evaluations.router)

setup_admin(app, engine)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={}
    )


@app.get("/tasks-page", response_class=HTMLResponse)
def tasks_page(request: Request):
    return templates.TemplateResponse(request=request, name="tasks.html", context={})


@app.get("/teams-page", response_class=HTMLResponse)
def teams_page(request: Request):
    return templates.TemplateResponse(request=request, name="teams.html", context={})


@app.get("/meetings-page", response_class=HTMLResponse)
def meetings_page(request: Request):
    return templates.TemplateResponse(request=request, name="meetings.html", context={})


@app.get("/evaluations-page", response_class=HTMLResponse)
def evaluations_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="evaluations.html", context={}
    )


@app.get("/calendar-page", response_class=HTMLResponse)
def calendar_page(request: Request):
    return templates.TemplateResponse(request=request, name="calendar.html", context={})


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

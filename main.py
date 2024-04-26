from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from database import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = User("users.db")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    hashed_password = pwd_context.hash(password)
    if not db.is_existence(username):
        db.add(username, hashed_password)
        return templates.TemplateResponse("login.html", {"request": request, "message": "Registration successful"})
    else:
        return templates.TemplateResponse("register.html", {"request": request, "message": "A user with the same name already exists"})

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    if db.is_existence(username) and pwd_context.verify(password, db.get_hash_password(username)):
        return templates.TemplateResponse("profile.html", {"request": request, "username": username})
    else:
        raise HTTPException(status_code=400, detail="Invalid username or password")

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, user_id: int):
    username = db.get_name_by_id(user_id)
    if username:
        return templates.TemplateResponse("profile.html", {"request": request, "username": username})
    else:
        raise HTTPException(status_code=404, detail="User not found")
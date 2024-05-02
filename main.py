from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from database import User
from itsdangerous import URLSafeTimedSerializer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = User("users.db")

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

SECRET_KEY = 'secret_key'
session_serializer = URLSafeTimedSerializer(SECRET_KEY)

def remove_session(response: RedirectResponse):
    response.delete_cookie('session')
    return response

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
        response = templates.TemplateResponse("profile.html", {"request": request, "username": username})
        session_token = session_serializer.dumps(username)
        response.set_cookie('session', session_token)
        return response
    else:
        raise HTTPException(status_code=400, detail="Invalid username or password")

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, username: str):
    session_token = request.cookies.get('session')
    if session_token:
        username = session_serializer.loads(session_token, max_age=86400)
        return templates.TemplateResponse("profile.html", {"request": request, "username": username})
    else:
        return RedirectResponse(url='/login')

@app.get("/logout")
def logout():
    response = RedirectResponse(url='/login')
    return remove_session(response)
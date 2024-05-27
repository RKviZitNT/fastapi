from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from database import User
from itsdangerous import URLSafeTimedSerializer

#создание объкта класса для хэширования данных
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#создание объекта для работы с базой данных
db = User("users.db")

#создание приложения для работы с API
app = FastAPI()

#добавление директории с развёртками страниц и статических директории файлов их оформления
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

#создание сида для хэширования данных
SECRET_KEY = 'secret_key'
session_serializer = URLSafeTimedSerializer(SECRET_KEY)

#функция удаления данных сессии
def remove_session(response: RedirectResponse):
    response.delete_cookie('session')
    return response

#получение домашней страницы
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#получение страницы регистрации
@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

#ввод и отправка данных на странице регистрации
@app.post("/register")
def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    #хэширование полученного пароля
    hashed_password = pwd_context.hash(password)
    #проверка на существование пользователя в БД
    if not db.is_existence(username):
        #добавление пользователя в БД
        db.add(username, hashed_password)
        return templates.TemplateResponse("login.html", {"request": request, "message": "Registration successful"})
    else:
        return templates.TemplateResponse("register.html", {"request": request, "message": "A user with the same name already exists"})

#получение страницы логина
@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#ввод и отправка данных на странице регистрации
@app.post("/login")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    #проверка на существование пользователя в БД
    if db.is_existence(username) and pwd_context.verify(password, db.get_hash_password(username)):
        response = templates.TemplateResponse("profile.html", {"request": request, "username": username})
        #создание пользовательской сессии
        session_token = session_serializer.dumps(username)
        #создание файлов cookie
        response.set_cookie('session', session_token)
        return response
    else:
        #возврат ошибки в случае неудачи
        raise HTTPException(status_code=400, detail="Invalid username or password")

#получение страницы профиля
@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, username: str):
    #получении пользовательской сессии
    session_token = request.cookies.get('session')
    if session_token:
        #открытие страницы если сессия успешна
        username = session_serializer.loads(session_token, max_age=86400)
        return templates.TemplateResponse("profile.html", {"request": request, "username": username})
    else:
        return RedirectResponse(url='/login')

#функция завершения пользовательской сессии
@app.get("/logout")
def logout():
    response = RedirectResponse(url='/login')
    return remove_session(response)
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

MONGO_URI = "mongodb+srv://mdb_fwapp_user:JOcwKQlrA7399cvO@cluster0.9srmi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["mdb_fastapi_webapp"]
users_collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "msg": ""})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = await users_collection.find_one({"username": username})
    if user and pwd_context.verify(password, user["password"]):
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Login successful!"})
    return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid credentials"})


@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    existing_user = await users_collection.find_one({"username": username})
    if existing_user:
        return {"error": "User already exists"}
    hashed_pw = pwd_context.hash(password)
    await users_collection.insert_one({"username": username, "password": hashed_pw})
    return {"msg": "User registered successfully"}

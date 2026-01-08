from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables, get_session
from route.users import router as users_router


from sqlmodel import Session, select



@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    create_db_and_tables()
    session: Session = next(get_session())
  
    yield  # l'app tourne ici




app = FastAPI(lifespan=lifespan)

# Configuration CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://13.39.13.72",
    "http://g3.finder-me.fr"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

app.include_router(users_router, prefix="/users")


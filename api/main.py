from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_and_tables, get_session
from .routes.users import router as users_router
from .routes.product import router as product_router



from sqlmodel import Session, select



@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    create_db_and_tables()
    session: Session = next(get_session())
  
    yield  # l'api tourne ici




app = FastAPI(lifespan=lifespan)

# Configuration CORS - Autoriser tous les domaines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

app.include_router(users_router, prefix="/users")
app.include_router(product_router, prefix="/product")

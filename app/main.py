from fastapi import FastAPI
from .database import db
from .routes import users, posts
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # loads the env file


# from .database import Base, engine

# Base.metadata.create_all(bind=engine)

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify http://localhost:4200
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(users.router)
api.include_router(posts.router)


@api.get("/")
async def index():
    try:
        server_info = await db.command("ping")
        return {"status": "MongoDB connected", "info": server_info}
    except Exception as e:
        return {"status": "MongoDB connection failed", "error": str(e)}

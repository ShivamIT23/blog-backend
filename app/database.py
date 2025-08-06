from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  # Store this in .env file
DB_NAME = os.getenv("DB_NAME")      # Store this in .env file

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

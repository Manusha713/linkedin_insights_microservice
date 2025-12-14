import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME")

client: Optional[AsyncIOMotorClient] = None
database = None

async def connect_to_mongo():
    global client, database
    if not DATABASE_URL or not DB_NAME:
        raise Exception("MongoDB configuration missing in .env")
        
    print("Attempting to connect to MongoDB...")
    try:
        client = AsyncIOMotorClient(DATABASE_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping') 
        database = client[DB_NAME]
        print(f"MongoDB connection successful. Connected to database '{DB_NAME}'.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

async def get_db_async():
    if database is None:
        raise Exception("Database connection not established.")
    yield database
import os

MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
MONGODB_PORT = os.environ.get("MONGODB_PORT", 27017)

MONGODB_USER = os.environ.get("MONGODB_USER", "root")
MONGODB_PASS = os.environ.get("MONGODB_PASS", "example")

MONGODB_DB = os.environ.get("MONGODB_DB", "mp_feedbacks_test")

MONGODB_URL = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}"

from motor.motor_asyncio import AsyncIOMotorClient

def get_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[MONGODB_DB]

def get_users_collection():
    database = get_database()
    collection = database['users']

    return collection


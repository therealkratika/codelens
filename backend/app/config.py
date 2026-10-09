
import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "codelens")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing. Add it to your backend .env file."
    )

mongo_client = MongoClient(
    MONGODB_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000,
)

database = mongo_client[MONGODB_DATABASE]
repositories_collection = database["repositories"]


def check_mongodb_connection():
    mongo_client.admin.command("ping")

    # Create the index only after a successful connection.
    repositories_collection.create_index(
        "normalized_url",
        unique=True,
    )

    return True

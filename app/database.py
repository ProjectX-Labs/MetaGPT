from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class DataBase:
    def __init__(self):
        self._client: AsyncIOMotorClient = None
        self._db = None

    async def connect(self, uri: str, dbname: str):
        self._client = AsyncIOMotorClient(uri)
        self._db = self._client[dbname]

    async def close(self):
        self._client.close()

    def __getitem__(self, item):
        return self._db[item]

db = DataBase()

async def connect_to_mongo():
    await db.connect("mongodb://localhost:27017", "projectx")

async def close_mongo_connection():
    await db.close()

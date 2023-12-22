import asyncpg

class PostgresDB:
    _instance = None
    _pool = None

    class PostgresConfig:
        POSTGRES_URL = "postgresql://postgres:admin_uptp@uptp.crc68fl0q7py.ap-south-1.rds.amazonaws.com:5432/uptp"

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._pool = await asyncpg.create_pool(cls.PostgresConfig.POSTGRES_URL)
        return cls._instance

    @classmethod
    async def get_pool(cls):
        if cls._instance is None:
            await cls.get_instance()
        return cls._pool

    @classmethod
    async def close_pool(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.postgres_config import PostgresDB
from routes.index import main_router as router

app = FastAPI()

# You should only add CORSMiddleware once, with the correct settings.
# Here, I'm assuming you want the specific origins listed.
origins = [
    "http://localhost.tiangolo.com",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://localhost:3000/",
    "http://localhost:3000",
    "http://192.168.0.117:3000"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    # Initialize the connection pool
    await PostgresDB.get_instance()

@app.on_event("shutdown")
async def shutdown_event():
    # Close the connection pool
    await PostgresDB.close_pool()


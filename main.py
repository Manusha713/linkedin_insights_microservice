from fastapi import FastAPI
from .database import connect_to_mongo, close_mongo_connection
from .routers import insights 


app = FastAPI(title="LinkedIn Insights Microservice (MongoDB)")

@app.on_event("startup")
async def on_startup():
    await connect_to_mongo()

@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()

# Placeholder route
@app.get("/")
def read_root():
    return {"message": "LinkedIn Insights Service (MongoDB/Async) is Running! Check /docs."}

app.include_router(insights.router)
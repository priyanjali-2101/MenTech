from fastapi import FastAPI
from database.db import Base, engine
from model import risk_table, user_table, comment_table, activity_table
from routers import risk_endpoints, user_endpoints, comment_endpoints

app = FastAPI(
    title="Risk Management System",
    description="Complete Backend API for managing risks",
    version="1.0.0"
)

# Saari tables banao
Base.metadata.create_all(bind=engine)

# Saare routers register karo
app.include_router(user_endpoints.router)
app.include_router(risk_endpoints.router)
app.include_router(comment_endpoints.router)


@app.get("/")
def home():
    return {"message": "Risk Management System is Running! "}
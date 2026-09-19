from fastapi import FastAPI
from credentials.routes import router as credentials_router

app = FastAPI()
app.include_router(credentials_router)

@app.get("/")
def home():
    return {"message": "Bienvenido a la API de registro de usuarios "}
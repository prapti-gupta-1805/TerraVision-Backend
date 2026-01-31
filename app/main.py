from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# import routers
from app.routes import firebase_test, simulation, layers, aqi, temp


app = FastAPI(
    title="Green Corridor Backend API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(firebase_test.router)
app.include_router(layers.router)
app.include_router(simulation.router)
app.include_router(aqi.router)
app.include_router(temp.router)

@app.get("/health")
def health():
    return {"ok": True}
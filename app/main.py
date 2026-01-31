from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import routers
from app.routes import layers, simulation, scenarios

app = FastAPI(
    title="Green Corridor Backend API",
    version="1.0.0"
)

# Allow frontend / Postman / hackathon demo calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register API routers
app.include_router(layers.router)
app.include_router(simulation.router)
app.include_router(scenarios.router)


# simple test route
@app.get("/health")
def health():
    return {"ok": True}
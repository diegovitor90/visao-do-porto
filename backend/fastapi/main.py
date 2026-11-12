
from fastapi import FastAPI

app = FastAPI(
    title="Visão do Porto - FastAPI",
    description="API experimental para comparação com Spring Boot",
    version="0.1.0"
)

@app.get("/api/health")
def health():
    return {
        "status": "UP",
        "service": "visao-do-porto-backend",
        "framework": "FastAPI"
    }

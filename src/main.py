# src/main.py
from fastapi import FastAPI
from .api.routes import budget, specs, reference, form

app = FastAPI(title="Auto QM Form")

app.include_router(budget.router)
app.include_router(specs.router)
app.include_router(reference.router)
app.include_router(form.router)

@app.get("/health")
def health():
    return {"status": "ok"}

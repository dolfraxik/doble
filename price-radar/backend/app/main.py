from fastapi import FastAPI

app = FastAPI(title="Price Radar API")

@app.get("/")
def read_root():
    return {"status": "working", "message": "Welcome to Price Radar API"}

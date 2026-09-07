from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Concurrent Order Fulfillment System"}

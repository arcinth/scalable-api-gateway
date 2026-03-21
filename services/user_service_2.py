from fastapi import FastAPI

app = FastAPI()

@app.get("/profile")
def get_profile():
    return {"service": "User Service 2", "data": "User Profile Data (Instance 2)"}
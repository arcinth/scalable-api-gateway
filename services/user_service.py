from fastapi import FastAPI

app = FastAPI()

@app.get("/profile")
def get_profile():
    return {"service": "User Service", "data": "User Profile Data"}
from fastapi import FastAPI

app = FastAPI()

@app.get("/orders")
def get_orders():
    return {"service": "Order Service", "data": "Order List"}
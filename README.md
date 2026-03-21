# Scalable API Gateway

A production-style API Gateway built using FastAPI, designed to route requests across multiple microservices with support for authentication, caching, and fault tolerance.

---

## Overview

This project demonstrates how modern backend systems handle scalability and reliability.
The gateway acts as a single entry point and forwards requests to multiple services while applying middleware for security, performance, and resilience.

---

## Key Features

* JWT-based authentication for secure access
* Rate limiting to prevent abuse
* Round-robin load balancing across service instances
* Redis-based caching to reduce response time
* Circuit breaker to handle service failures gracefully
* Modular microservices structure (user and order services)

---

## Architecture

Client → API Gateway → Services → Response

The gateway is responsible for:

* Routing requests dynamically
* Managing authentication and rate limits
* Improving performance through caching
* Handling failures using circuit breaker logic

---

## Tech Stack

* FastAPI
* Python
* Redis
* Docker (for Redis)

---

## Running the Project

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start Redis

```bash
docker run -d -p 6379:6379 redis
```

### Start services

```bash
python -m uvicorn services.user_service:app --port 8001
python -m uvicorn services.user_service_2:app --port 8003
python -m uvicorn services.order_service:app --port 8002
```

### Start gateway

```bash
python -m uvicorn gateway.main:app --port 8000
```

---

## Testing

Open:

```
http://localhost:8000/docs
```

* Generate token using `/login`
* Use Postman or curl to test protected endpoints

---

## Performance Note

The first request is processed by the service, while repeated requests are served from Redis cache, significantly reducing response time.

---

## What I Learned

* Designing an API Gateway pattern
* Implementing middleware for real-world systems
* Handling service failures using circuit breaker
* Improving performance using caching
* Structuring microservices in a scalable way

---

## Author

Arcinth Siva

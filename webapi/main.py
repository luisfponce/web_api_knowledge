from fastapi import FastAPI
import uvicorn
from api.routers import api_router
# from api.endpoints.v1 import auths, users, prompts

tags_metadata = [
    {
        "name": "Auth",
        "description": "Authentication operations (login, signup, password recovery).",
    },
    {
        "name": "Users",
        "description": "Operations with users (CRUD).",
    },
    {
        "name": "Prompts",
        "description": "Operations with prompts.",
    },
]

myapp = FastAPI(
    title="Portfolio API",
    description="API for managing users, prompts, and authentication in a web environment.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata
)


@myapp.get("/")
def root():
    return {"Portfolio App": "This is a simple app using FastAPI and mariadb."}


# Include all API routes
myapp.include_router(api_router, prefix="/api/v1", tags=["api"])

# Include routers
"""
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
app.include_router(auths.router, prefix="/auth", tags=["Auth"])
"""

if __name__ == "__main__":
    uvicorn.run(myapp, host="127.0.0.1", port=8000)

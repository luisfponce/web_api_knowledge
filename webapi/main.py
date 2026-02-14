from fastapi import FastAPI
import uvicorn
from api.routers import api_router
# from api.endpoints.v1 import auths, users, cards

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
        "name": "Cards",
        "description": "Operations with cards.",
    },
]

myapp = FastAPI(
    title="Bank API",
    description="API for managing users, cards, and authentication in a banking system.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata
)

"""
Create a MariaDB container for testing purposes.
You can run this command in your terminal to start a MariaDB server with the specified environment variables
and port mapping. Make sure Docker is installed and running on your machine.
docker run --detach \
  --env MARIADB_USER=pbtest \
  --env MARIADB_PASSWORD=pbtest \
  --env MARIADB_DATABASE=bank_db \
  --env MARIADB_RANDOM_ROOT_PASSWORD=1 \
  --name mariadb-server-test \
  -p 3306:3306 \
  mariadb:latest

Ensure that the environment variable DB_URL is set to your MariaDB connection string
Example: export DB_URL="mariadb+mariadbconnector://pbtest:pbtest@127.0.0.1:3306/bank_db"
"""

@myapp.get("/")
def root():
    return {"Bank App": "This is a simple app using FastAPI and mariadb."}


# Include all API routes
myapp.include_router(api_router, prefix="/api/v1", tags=["api"])

# Include routers
"""
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(cards.router, prefix="/cards", tags=["Cards"])
app.include_router(auths.router, prefix="/auth", tags=["Auth"])
"""

if __name__ == "__main__":
    uvicorn.run(myapp, host="127.0.0.1", port=8000)
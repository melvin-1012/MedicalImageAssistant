from fastapi import FastAPI
from .api_router import router

# This file is just for standalone testing.
# Person 2 (Backend) will NOT run this file; they will just import the router into their own FastAPI app.
app = FastAPI(
    title="GenAI Module Standalone Test Server",
    description="A temporary server to test the GenAI router and view the Swagger UI."
)

app.include_router(router)

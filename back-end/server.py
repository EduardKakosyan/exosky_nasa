from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Mount the static files from the dist folder
app.mount("/assets", StaticFiles(directory="app/dist/assets"), name="static")


# Serve the index.html for the root path
@app.get("/")
async def read_root():
    return FileResponse("app/dist/index.html")


# Serve index.html for any other path not found (for SPA routing)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if os.path.isfile(f"app/dist/{full_path}"):
        return FileResponse(f"app/dist/{full_path}")
    return FileResponse("app/dist/index.html")


# Your API routes go here
@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

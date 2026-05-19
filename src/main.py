import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.routes import router, update_metrics
from src.daemon.watcher import setup_observer

# Global variable to hold our background watcher
vfs_observer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Start the Watchdog Observer on boot
    print("\n[System] Starting VFS Watcher in the background...")
    global vfs_observer
    vfs_observer = setup_observer("./local_repo", log_callback=update_metrics)
    vfs_observer.start()
    
    yield # The FastAPI server runs while this is yielding
    
    # 2. Shut down the Watchdog Observer gracefully on exit
    print("\n[System] Shutting down VFS Watcher...")
    vfs_observer.stop()
    vfs_observer.join()

# Initialize the FastAPI app
app = FastAPI(title="VFS Prefetch API", lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    print("\n" + "="*55)
    print("🚀 Booting VFS Enterprise Predictive Platform")
    print("Dashboard will be live at: http://127.0.0.1:8000")
    print("="*55)
    
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=False)
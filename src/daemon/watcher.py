import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.analytics.engine import PredictionEngine
from src.daemon.prefetcher import VFSPrefetcher # <--- Import the Hands

class VFSHandler(FileSystemEventHandler):
    def __init__(self, engine: PredictionEngine, repo_name: str, log_callback=None):
        self.engine = engine
        self.repo_name = repo_name
        self.log_callback = log_callback
        
        # Initialize the Prefetcher (The Hands)
        self.prefetcher = VFSPrefetcher(log_callback=log_callback)

    def process_event(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path.replace("\\", "/") 
        if self.repo_name in filepath:
            relative_path = filepath.split(f"{self.repo_name}/")[-1]
            
            detect_msg = f"Detected interaction with: {relative_path}"
            print(f"\n[Daemon] {detect_msg}")
            if self.log_callback:
                self.log_callback("event", detect_msg)
            
            predictions = self.engine.predict(relative_path)
            
            # Hand the predictions over to the Prefetcher!
            if predictions:
                self.prefetcher.hydrate(predictions)

    def on_modified(self, event):
        self.process_event(event)

    def on_created(self, event):
        self.process_event(event)

def setup_observer(path_to_watch: str = "./local_repo", log_callback=None):
    """Initializes the observer without blocking the main thread."""
    if not os.path.exists(path_to_watch):
        os.makedirs(path_to_watch)
        
    engine = PredictionEngine("data/mock_hydration_logs.csv")
    event_handler = VFSHandler(engine, repo_name=path_to_watch.strip("./"), log_callback=log_callback)
    
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    return observer

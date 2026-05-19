from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# In-memory database to hold telemetry state
app_state = {
    "events": 0,
    "prefetches": 0,
    "logs": []
}

def update_metrics(event_type: str, message: str):
    """Callback used by the Watcher to update the dashboard."""
    if event_type == "event":
        app_state["events"] += 1
    elif event_type == "prefetch":
        app_state["prefetches"] += 1
    
    app_state["logs"].insert(0, message)
    app_state["logs"] = app_state["logs"][:15] # Keep the last 15 logs

@router.get("/", response_class=HTMLResponse)
def get_dashboard():
    # Format the logs into HTML list items
    logs_html = "".join([f"<li style='margin-bottom: 8px;'>[SYSTEM] {log}</li>" for log in app_state['logs']])
    if not logs_html:
        logs_html = "<li>Waiting for file events... Try editing a file in the local_repo/ folder.</li>"
        
    return f"""
    <html>
        <head><title>VFS Prefetch Dashboard</title></head>
        <body style="font-family: Segoe UI, Arial, sans-serif; padding: 40px; background-color: #f4f4f9;">
            <h1 style="color: #333;">🚀 VFS Predictive Prefetching Dashboard</h1>
            <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 220px;">
                    <h2 style="margin: 0; font-size: 2.5rem; color: #0078D4;">{app_state['events']}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: bold;">Manual File Reads</p>
                </div>
                <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 220px;">
                    <h2 style="margin: 0; font-size: 2.5rem; color: #107C10;">{app_state['prefetches']}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: bold;">Files Prefetched (Zero Latency)</p>
                </div>
            </div>
            <h3 style="color: #333;">Live Telemetry Stream</h3>
            <ul style="background: #1E1E1E; color: #5CE6CD; padding: 20px; border-radius: 8px; list-style-type: none; font-family: monospace; min-height: 200px;">
                {logs_html}
            </ul>
            <script>
                // Auto-refresh the UI every 1.5 seconds
                setTimeout(function(){{ location.reload(); }}, 1500);
            </script>
        </body>
    </html>
    """
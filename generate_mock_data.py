import csv
import random
from datetime import datetime, timedelta

# Define realistic file access patterns (co-occurrences)
WORKFLOWS = {
    "auth_feature": ["src/auth/login.py", "tests/test_login.py", "config/auth_schema.json"],
    "ui_update": ["src/ui/button.tsx", "src/ui/theme.css", "tests/button.spec.ts"],
    "payment_gateway": ["src/billing/stripe.py", "src/billing/models.py", "tests/test_billing.py"],
    "random_exploration": ["README.md", "package.json", "src/main.py", "docs/architecture.md"]
}

def generate_telemetry(num_sessions=300):
    start_time = datetime.now() - timedelta(days=30)
    logs = []

    for _ in range(num_sessions):
        # Pick a random workflow
        workflow_name = random.choice(list(WORKFLOWS.keys()))
        files_to_hydrate = WORKFLOWS[workflow_name]
        
        # Simulate a developer session
        dev_id = f"dev_{random.randint(100, 105)}"
        
        for file_path in files_to_hydrate:
            # Add a slight delay (1 to 5 seconds) between file reads
            start_time += timedelta(seconds=random.randint(1, 5))
            
            # 10% chance a file is skipped (simulating it's already in local cache)
            if random.random() > 0.1:
                logs.append({
                    "timestamp": start_time.isoformat(),
                    "developer_id": dev_id,
                    "file_path": file_path,
                    "action": "hydrated"
                })

    return logs

def save_to_csv(logs, filename="data/mock_hydration_logs.csv"):
    keys = logs[0].keys()
    with open(filename, "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(logs)
    print(f"Successfully generated {len(logs)} telemetry events in {filename}")

if __name__ == "__main__":
    generated_logs = generate_telemetry(num_sessions=500)
    save_to_csv(generated_logs)
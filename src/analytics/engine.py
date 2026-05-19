import pandas as pd

class PredictionEngine:
    def __init__(self, data_path: str = "data/mock_hydration_logs.csv"):
        self.data_path = data_path
        self.transition_matrix = {}
        self._build_matrix()

    def _build_matrix(self):
        """Builds a conditional probability matrix from VFS telemetry."""
        print("[Analytics] Crunching telemetry logs...")
        
        try:
            # 1. Load the telemetry logs
            df = pd.read_csv(self.data_path)
        except FileNotFoundError:
            print("[Analytics] Warning: No telemetry data found.")
            return

        # 2. Ensure timestamps are strictly ordered for time-series analysis
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by=['developer_id', 'timestamp'])

        # 3. Shift data to find the 'next' file hydrated by the same developer
        df['next_file'] = df.groupby('developer_id')['file_path'].shift(-1)

        # Drop the last action of each session (since there is no 'next' file)
        df = df.dropna(subset=['next_file'])

        # 4. Calculate raw co-occurrence frequencies
        transitions = df.groupby(['file_path', 'next_file']).size().reset_index(name='count')

        # 5. Convert counts to mathematical probabilities
        total_transitions = transitions.groupby('file_path')['count'].transform('sum')
        transitions['probability'] = transitions['count'] / total_transitions

        # 6. Store as a nested dictionary for instant O(1) lookups in the daemon
        # Structure: { 'fileA': {'fileB': 0.85, 'fileC': 0.15} }
       # Change lines 40-42 to look exactly like this:
        self.transition_matrix = transitions.sort_values(
            ['file_path', 'probability'], ascending=[True, False]
        ).groupby('file_path').apply(
            lambda x: dict(zip(x['next_file'], x['probability'])),
            include_groups=False  # <--- This fixes the warning
        ).to_dict()
        
        print(f"[Analytics] Matrix built successfully. Tracking {len(self.transition_matrix)} unique files.")

    def predict(self, current_file: str, top_n: int = 2) -> list:
        """Returns the top N most likely files to be hydrated next."""
        if not self.transition_matrix or current_file not in self.transition_matrix:
            return []
        
        predictions = self.transition_matrix[current_file]
        # Extract just the file paths, sliced to the requested limit
        return list(predictions.keys())[:top_n]

if __name__ == "__main__":
    # Fixed path: Since you are running from the root folder, 
    # the path to the data folder is just "data/..."
    engine = PredictionEngine("data/mock_hydration_logs.csv")
    test_file = "src/auth/login.py"
    print(f"\n--- Prediction Test ---")
    print(f"When a developer opens '{test_file}', they will likely need:")
    for prediction in engine.predict(test_file):
        print(f" -> {prediction}")
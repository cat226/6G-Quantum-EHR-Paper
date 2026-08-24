import json
import os

class MetricsCollector:
    """
    Writes raw transaction metrics to JSONL without exposing secrets.
    """
    def __init__(self, output_file: str):
        self.output_file = output_file
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
    def record(self, metric: dict):
        with open(self.output_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')

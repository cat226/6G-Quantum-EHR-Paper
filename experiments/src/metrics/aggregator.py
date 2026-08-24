import json
import csv
import os
import statistics
from collections import defaultdict
import glob

class MetricsAggregator:
    """
    Aggregates JSONL raw results into CSV summaries.
    """
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def aggregate(self):
        files = glob.glob(os.path.join(self.input_dir, "*.jsonl"))
        
        # Group metrics by cell configuration
        # Key: (baseline, qkd_availability, device_count, payload_class, network_load)
        grouped_data = defaultdict(lambda: {
            "latencies": [],
            "ke_latencies": [],
            "auth_latencies": [],
            "enc_latencies": [],
            "total_runs": 0,
            "successes": 0,
            "failures": 0,
            "modes": defaultdict(int)
        })
        
        for file in files:
            with open(file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    key = (
                        data["baseline"],
                        data["qkd_availability"],
                        data["device_count"],
                        data["payload_class"],
                        data["network_load"]
                    )
                    
                    g = grouped_data[key]
                    g["total_runs"] += 1
                    
                    if data["success"]:
                        g["successes"] += 1
                        g["latencies"].append(data["latency_ms"])
                        g["ke_latencies"].append(data["key_establishment_latency_ms"])
                        g["auth_latencies"].append(data["authentication_latency_ms"])
                        g["enc_latencies"].append(data["encryption_latency_ms"])
                    else:
                        g["failures"] += 1
                        
                    g["modes"][data["selected_mode"]] += 1
                    
        # Write CSV
        output_file = os.path.join(self.output_dir, "aggregated_results.csv")
        headers = [
            "baseline", "qkd_availability", "device_count", "payload_class", "network_load",
            "total_runs", "success_rate", "failure_rate",
            "mean_latency_ms", "median_latency_ms", "stdev_latency_ms", "p95_latency_ms",
            "mean_ke_latency_ms", "mean_auth_latency_ms", "mean_enc_latency_ms",
            "mode_distribution"
        ]
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for key, g in grouped_data.items():
                latencies = g["latencies"]
                n_success = len(latencies)
                
                mean_lat = statistics.mean(latencies) if n_success > 0 else 0.0
                med_lat = statistics.median(latencies) if n_success > 0 else 0.0
                stdev_lat = statistics.stdev(latencies) if n_success > 1 else 0.0
                
                if n_success > 0:
                    sorted_lat = sorted(latencies)
                    p95_idx = int(0.95 * n_success)
                    p95_lat = sorted_lat[p95_idx if p95_idx < n_success else -1]
                else:
                    p95_lat = 0.0
                    
                mean_ke = statistics.mean(g["ke_latencies"]) if n_success > 0 else 0.0
                mean_auth = statistics.mean(g["auth_latencies"]) if n_success > 0 else 0.0
                mean_enc = statistics.mean(g["enc_latencies"]) if n_success > 0 else 0.0
                
                mode_dist = "|".join([f"{k}:{v}" for k, v in g["modes"].items()])
                
                writer.writerow([
                    key[0], key[1], key[2], key[3], key[4],
                    g["total_runs"],
                    g["successes"] / g["total_runs"] if g["total_runs"] > 0 else 0,
                    g["failures"] / g["total_runs"] if g["total_runs"] > 0 else 0,
                    mean_lat, med_lat, stdev_lat, p95_lat,
                    mean_ke, mean_auth, mean_enc,
                    mode_dist
                ])

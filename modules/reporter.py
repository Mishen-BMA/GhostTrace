import json
import datetime

def save_report(target: str, target_type: str, results: dict, filepath: str):
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    report = {
        "tool":      "GhostTrace v1.0",
        "timestamp": timestamp,
        "target":    target,
        "type":      target_type,
        "results":   results
    }

    if filepath.endswith(".json"):
        with open(filepath, "w") as f:
            json.dump(report, f, indent=4)
    else:
        with open(filepath, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("  GHOSTTRACE OSINT REPORT\n")
            f.write(f"  Generated : {timestamp}\n")
            f.write(f"  Target    : {target} [{target_type.upper()}]\n")
            f.write("=" * 60 + "\n\n")
            f.write(json.dumps(results, indent=4))
            f.write("\n\n[GhostTrace] End of Report\n")
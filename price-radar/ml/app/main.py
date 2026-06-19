import time
import sys

print("ML Service started successfully!", flush=True)

try:
    while True:
        print("ML-Service: Checking prices radar...", flush=True)
        time.sleep(10)
except KeyboardInterrupt:
    print("ML Service stopped.")
    sys.exit(0)

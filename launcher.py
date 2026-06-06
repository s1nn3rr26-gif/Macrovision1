import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ])
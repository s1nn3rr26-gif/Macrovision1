import subprocess
import sys
import os

if __name__ == "__main__":
    # Asegurar que estamos en el directorio correcto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ])
# danger.py - Intentionally insecure code for testing security scanners

import os
import pickle
import subprocess
import requests
import webbrowser  # Unused import

# [CRITICAL] Code Injection
def execute_code(user_input):
    result = eval(user_input)  # Can execute arbitrary code
    return result

# [CRITICAL] Command Injection
def delete_everything():
    os.system("rm -rf /")  # Dangerous system command

# [CRITICAL] Shell Injection
def run_command(cmd):
    subprocess.call(cmd, shell=True)  # shell=True is unsafe

# [CRITICAL] Deserialization Attack
def load_data():
    with open("data.pkl", "rb") as f:
        data = pickle.load(f)  # Unsafe deserialization
    return data

# [MEDIUM] Hardcoded Secrets
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin@123"
JWT_SECRET = "mysecretkey123"

# [MEDIUM] Insecure HTTP Request
def send_request():
    requests.get("http://api.example.com/data")  # Uses HTTP instead of HTTPS

# [LOW] Debug Statements
def process():
    print("Processing started...")  # Should use logging
    # TODO: Add error handling
    # FIXME: This function is incomplete

if __name__ == "__main__":
    delete_everything()

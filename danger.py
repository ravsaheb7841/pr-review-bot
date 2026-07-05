# danger.py - Intentionally insecure code for security testing

import os
import pickle
import subprocess
import requests
import webbrowser  # Unused import

# 1. Command Injection Risk
def delete_everything():
    os.system("rm -rf /")  # Deletes all files on Unix-like systems

# 2. Code Injection Risk
def execute_user_code(code):
    exec(code)  # Executes arbitrary code

# 3. Deserialization Attack
def load_malicious_data():
    with open("malicious.pkl", "rb") as f:
        data = pickle.load(f)  # Can execute malicious code
    return data

# 4. SQL Injection
def get_user(name):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    print(query)

# 5. Hardcoded Secrets
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
DATABASE_PASSWORD = "admin123"
API_TOKEN = "ghp_1234567890abcdef"

# 6. Insecure Network Request
def send_data():
    requests.get("http://example.com/api?data=sensitive")

# 7. Dangerous Function
def run_subprocess(cmd):
    subprocess.call(cmd, shell=True)

# 8. Debug Code Left Behind
print("DEBUG: Database password is admin123")

# 9. TODO / FIXME
# TODO: Remove this before production
# FIXME: Security hole here!

if __name__ == "__main__":
    delete_everything()
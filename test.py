# test.py - Security issues for testing
import os

def process_data(user_input):
    # Dangerous! Uses eval()
    result = eval(user_input)
    return result

def delete_all():
    # Dangerous! Uses os.system()
    os.system("rm -rf /")

# Hardcoded secret
API_KEY = "sk-1234567890"

def main():
    print("Starting process...")
    # TODO: Add error handling
    pass

if __name__ == "__main__":
    main()
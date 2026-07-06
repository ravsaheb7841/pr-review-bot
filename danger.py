# danger.py
"""
Sample application containing intentionally insecure code.

Purpose:
This file is used for testing automated security review tools,
static analyzers, and GitHub PR Review Bots.

DO NOT USE IN PRODUCTION.
"""

import os
import pickle
import subprocess
import requests


class SecurityTestApplication:
    """Application used for security scanner testing."""

    def execute_user_expression(self, expression: str):
        """
        Intentionally vulnerable:
        Uses eval() on user input.
        """
        return eval(expression)

    def execute_system_command(self, command: str):
        """
        Intentionally vulnerable:
        Executes a shell command.
        """
        os.system(command)

    def execute_shell_process(self, command: str):
        """
        Intentionally vulnerable:
        Uses shell=True.
        """
        subprocess.run(command, shell=True)

    def load_serialized_object(self, filename: str):
        """
        Intentionally vulnerable:
        Unsafe pickle deserialization.
        """
        with open(filename, "rb") as file:
            return pickle.load(file)

    def fetch_remote_data(self):
        """
        Intentionally vulnerable:
        Uses insecure HTTP.
        """
        return requests.get("http://api.example.com/data")


# ------------------------------------------------------------------
# Intentionally hardcoded secrets for scanner validation
# ------------------------------------------------------------------

API_KEY = "sk-test-1234567890"
DATABASE_PASSWORD = "admin123"
JWT_SECRET = "sample-secret-key"


def debug_operation():
    """Debug function used for scanner validation."""

    print("Application started")

    # TODO: Replace print() with logging.
    # FIXME: Add exception handling.

    return True


if __name__ == "__main__":
    app = SecurityTestApplication()

    app.execute_user_expression("2 + 2")
    app.execute_system_command("echo Testing")
    app.execute_shell_process("dir")
    debug_operation()
# 🤖 PR Review Bot

<p align="center">
  <strong>An AI-powered GitHub Pull Request Review Bot that automatically detects security vulnerabilities and code quality issues.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Latest-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT">
</p>

---

## 📖 Overview

PR Review Bot automatically reviews GitHub Pull Requests and identifies potential security vulnerabilities, hardcoded secrets, and code quality issues before code is merged.

Instead of manually reviewing every Pull Request, the bot performs automated analysis and posts a detailed review comment directly on GitHub.

---

# ✨ Features

- 🔴 Detects dangerous functions like `eval()`, `exec()`, `os.system()`, `pickle.load()`, and `subprocess(shell=True)`
- 🟡 Detects hardcoded API keys, passwords, tokens, and secrets
- 🟢 Finds code quality issues such as `print()` statements, TODOs, and FIXMEs
- ⚡ Automatically reviews Pull Requests using GitHub Webhooks
- 💬 Posts review comments directly on Pull Requests
- 📂 Supports scanning multiple changed files

---

# 🏗️ Architecture

```text
Developer
     │
     ▼
Create Pull Request
     │
     ▼
GitHub Webhook
     │
     ▼
FastAPI Server
     │
     ▼
Security & Quality Scanner
     │
     ▼
Generate Review Report
     │
     ▼
Comment on Pull Request
```

---

# 🛠️ Tech Stack

- Python
- FastAPI
- PyGithub
- GitHub Apps
- GitHub Webhooks
- ngrok

---

# 📂 Project Structure

```text
pr-review-bot/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
├── .env
└── private-key.pem
```

---

# 🚀 Installation

Clone the repository.

```bash
git clone https://github.com/ravsaheb7841/pr-review-bot.git

cd pr-review-bot
```

Create a virtual environment.

### Windows

```bash
python -m venv pr_bot_env

pr_bot_env\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv pr_bot_env

source pr_bot_env/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# ⚙️ Environment Variables

Create a `.env` file.

```env
GITHUB_APP_ID=

GITHUB_WEBHOOK_SECRET=

GITHUB_TOKEN=
```

---

# ▶️ Run the Project

Start FastAPI.

```bash
uvicorn main:app --reload
```

Start ngrok.

```bash
ngrok http 8000
```

Update your GitHub App webhook URL with the generated HTTPS URL.

---

# 🧪 Example Scan

Example vulnerable code:

```python
def process(data):
    return eval(data)

API_KEY = "sk-test"

print("Hello")
```

Example bot output:

```text
🔴 eval() detected
Risk: Code Injection

🟡 Hardcoded API Key detected

🟢 print() statement detected

Total Issues Found: 3
```

---

# 🔒 Security Checks

The bot currently detects:

- eval()
- exec()
- os.system()
- pickle.load()
- subprocess(shell=True)
- Hardcoded API Keys
- Passwords
- Tokens
- AWS Keys
- HTTP requests
- print() statements
- TODO comments
- FIXME comments

---

# 🚀 Future Improvements

- AI-generated fix suggestions
- Inline Pull Request comments
- Multi-language support
- Docker deployment
- GitHub Actions integration
- Security score dashboard

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Ravsaheb Bansode**

GitHub: https://github.com/ravsaheb7841

LinkedIn: https://www.linkedin.com/in/ravsaheb-bansode/

---

<p align="center">
⭐ If you found this project useful, please consider giving it a star.
</p>
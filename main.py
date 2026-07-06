import json
import hmac
import hashlib
import re
import os
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
import uvicorn
from dotenv import load_dotenv
from github import Github

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Config
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --------------------------------------------
# 1. Webhook Signature Verification
# --------------------------------------------
def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature for security"""
    if not signature or not signature.startswith('sha256='):
        return False
    expected = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# --------------------------------------------
# 2. Get Code Files from PR
# --------------------------------------------
def get_code_files(pr):
    """Extract code files (Python, JS, Java) from PR"""
    files = []
    code_extensions = ['.py', '.js', '.java', '.go', '.rs', '.cpp', '.c', '.h']
    for file in pr.get_files():
        if any(file.filename.endswith(ext) for ext in code_extensions):
            try:
                content = pr.base.repo.get_contents(file.filename, ref=pr.head.sha)
                files.append({
                    'filename': file.filename,
                    'content': content.decoded_content.decode(),
                    'additions': file.additions,
                    'deletions': file.deletions,
                    'status': file.status
                })
            except:
                continue
    return files

# --------------------------------------------
# 3. Security Scan Engine
# --------------------------------------------
def security_scan(code: str, filename: str) -> tuple:
    """Scan code for security issues and return issues with severity counts"""
    issues = []
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    
    # [CRITICAL] patterns
    critical_patterns = [
        (r'eval\s*\(', "[CRITICAL] eval() use — code injection risk"),
        (r'exec\s*\(', "[CRITICAL] exec() use — code injection risk"),
        (r'os\.system\s*\(', "[CRITICAL] os.system() — command injection risk"),
        (r'os\.popen\s*\(', "[CRITICAL] os.popen() — command injection risk"),
        (r'subprocess\.(call|Popen|run)\s*\([^)]*shell\s*=\s*True', "[CRITICAL] subprocess with shell=True — shell injection risk"),
        (r'pickle\.(load|loads)', "[CRITICAL] pickle — deserialization attack risk"),
        (r'__import__\s*\(', "[CRITICAL] Dynamic imports — security risk"),
    ]
    for pattern, message in critical_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"File `{filename}`: {message}")
            severity_counts["CRITICAL"] += 1
    
    # [HIGH] patterns
    high_patterns = [
        (r'os\.system\s*\(', "[HIGH] os.system() — command injection risk"),
        (r'os\.popen\s*\(', "[HIGH] os.popen() — command injection risk"),
    ]
    for pattern, message in high_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"File `{filename}`: {message}")
            severity_counts["HIGH"] += 1
    
    # [MEDIUM] patterns
    medium_patterns = [
        (r'API_KEY\s*=\s*["\']([A-Za-z0-9_\-]+)["\']', "[MEDIUM] Hardcoded API_KEY found"),
        (r'SECRET\s*=\s*["\']([A-Za-z0-9_\-]+)["\']', "[MEDIUM] Hardcoded SECRET found"),
        (r'PASSWORD\s*=\s*["\']([A-Za-z0-9_\-]+)["\']', "[MEDIUM] Hardcoded PASSWORD found"),
        (r'token\s*=\s*["\']([A-Za-z0-9_\-]+)["\']', "[MEDIUM] Hardcoded token found"),
        (r'requests\.get\s*\(["\']http://', "[MEDIUM] Insecure HTTP request (use HTTPS)"),
    ]
    for pattern, message in medium_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"File `{filename}`: {message}")
            severity_counts["MEDIUM"] += 1
    
    # [LOW] patterns
    low_patterns = [
        (r'print\s*\(', "[LOW] print() found — use logging instead"),
        (r'console\.log\s*\(', "[LOW] console.log() found — use logging instead"),
    ]
    for pattern, message in low_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"File `{filename}`: {message}")
            severity_counts["LOW"] += 1
    
    # [INFO] patterns
    info_patterns = [
        (r'TODO', "[INFO] TODO comment found — address before merge"),
        (r'FIXME', "[INFO] FIXME comment found — fix before merge"),
    ]
    for pattern, message in info_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"File `{filename}`: {message}")
            severity_counts["INFO"] += 1
    
    return issues, severity_counts

# --------------------------------------------
# 4. Generate Review Report
# --------------------------------------------
def generate_review_report(pr_title: str, pr_body: str, files: list) -> str:
    """Generate PR review report with severity counts"""
    report = f"## PR Review Report\n\n"
    report += f"**Title:** {pr_title}\n\n"
    if pr_body:
        report += f"**Description:** {pr_body[:200]}...\n\n"
    report += f"**Files Changed:** {len(files)}\n\n"
    report += "### Modified Files:\n"
    for f in files:
        report += f"- `{f['filename']}` (+{f['additions']} / -{f['deletions']}) [{f['status']}]\n"
    report += "\n---\n\n"
    report += "## Security Scan Results\n\n"
    
    total_issues = 0
    total_severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    
    for file in files:
        report += f"### File: `{file['filename']}`\n\n"
        issues, severity_counts = security_scan(file['content'], file['filename'])
        
        if issues:
            total_issues += len(issues)
            for severity in total_severity_counts:
                total_severity_counts[severity] += severity_counts[severity]
            for issue in issues:
                report += f"- {issue}\n"
        else:
            report += "- No security issues detected.\n"
        report += "\n"
    
    # Summary section with severity breakdown
    report += "---\n\n"
    report += "## Review Summary\n\n"
    
    if total_issues == 0:
        report += "No security issues were detected.\n\n"
    else:
        report += f"**Total Issues Detected:** {total_issues}\n\n"
        report += "### Severity Breakdown:\n"
        report += f"- **CRITICAL**: {total_severity_counts['CRITICAL']}\n"
        report += f"- **HIGH**: {total_severity_counts['HIGH']}\n"
        report += f"- **MEDIUM**: {total_severity_counts['MEDIUM']}\n"
        report += f"- **LOW**: {total_severity_counts['LOW']}\n"
        report += f"- **INFO**: {total_severity_counts['INFO']}\n"
        report += "\n"
    
    report += "---\n"
    report += "*This review was automatically generated by PR Review Bot.*\n"
    return report

# --------------------------------------------
# 5. Background Review Processor
# --------------------------------------------
def process_review(repo_full_name: str, pr_number: int, pr_title: str, pr_body: str):
    """Process review in background"""
    try:
        print(f"[INFO] Processing PR #{pr_number} in {repo_full_name}")
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        files = get_code_files(pr)
        if not files:
            pr.create_issue_comment("[INFO] No code files found to review.")
            return
        print(f"[INFO] Reviewing {len(files)} modified file(s)")
        report = generate_review_report(pr_title, pr_body, files)
        pr.create_issue_comment(report)
        print(f"[PASSED] Review posted on PR #{pr_number}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(f"[ERROR] Error while reviewing: {str(e)}")
        except:
            pass

# --------------------------------------------
# 6. Webhook Endpoint
# --------------------------------------------
@app.post("/webhook")
async def webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None)
):
    # 1. Verify signature
    payload = await request.body()
    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 2. Check if it's a PR event
    if x_github_event != "pull_request":
        return {"status": "ignored", "event": x_github_event}
    
    # 3. Parse payload
    data = json.loads(payload)
    action = data.get("action")
    
    # 4. Process only opened/synchronize/edited events
    if action not in ["opened", "synchronize", "edited"]:
        return {"status": "ignored", "action": action}
    
    pr = data["pull_request"]
    repo_full_name = data["repository"]["full_name"]
    pr_number = pr["number"]
    pr_title = pr["title"]
    pr_body = pr.get("body") or ""
    
    # 5. Background task
    background_tasks.add_task(
        process_review,
        repo_full_name,
        pr_number,
        pr_title,
        pr_body
    )
    return {"status": "review_scheduled", "pr": pr_number}

# --------------------------------------------
# 7. Health Check Endpoints
# --------------------------------------------
@app.get("/")
async def root():
    return {"message": "PR Review Bot is running!", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# --------------------------------------------
# 8. Main Entry Point
# --------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
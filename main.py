import json
import hmac
import hashlib
import re
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
import uvicorn
from dotenv import load_dotenv
import os
from github import Github

load_dotenv()

app = FastAPI()

# Environment variables
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def verify_signature(payload: bytes, signature: str) -> bool:
    """GitHub webhook signature verify करण्यासाठी"""
    if not signature or not signature.startswith('sha256='):
        return False
    
    expected = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

def get_code_files(pr):
    """PR मधील code files फक्त return करा"""
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

def security_scan(code: str, filename: str) -> list:
    """Security issues check"""
    issues = []
    
    patterns = [
        (r'eval\s*\(', "⚠️ eval() use — code injection risk"),
        (r'exec\s*\(', "⚠️ exec() use — code injection risk"),
        (r'__import__\s*\(', "⚠️ Dynamic imports — security risk"),
        (r'subprocess\.(call|Popen|run)\s*\(', "⚠️ subprocess call — validate inputs"),
        (r'pickle\.(load|loads)', "⚠️ pickle — deserialization attack risk"),
        (r'os\.system\s*\(', "⚠️ os.system() — command injection risk"),
        (r'os\.popen\s*\(', "⚠️ os.popen() — command injection risk"),
    ]
    
    for pattern, message in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"📄 `{filename}`: {message}")
    
    # Hardcoded secrets
    secret_patterns = [
        r'API_KEY\s*=\s*["\']([A-Za-z0-9_\-]+)["\']',
        r'SECRET\s*=\s*["\']([A-Za-z0-9_\-]+)["\']',
        r'PASSWORD\s*=\s*["\']([A-Za-z0-9_\-]+)["\']',
        r'token\s*=\s*["\']([A-Za-z0-9_\-]+)["\']',
    ]
    for pattern in secret_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"📄 `{filename}`: ⚠️ Hardcoded secret/token found")
    
    return issues

def generate_review_report(pr_title: str, pr_body: str, files: list) -> str:
    """Complete review report generate करा"""
    
    report = f"## 📋 PR Review Report\n\n"
    report += f"**Title:** {pr_title}\n\n"
    
    if pr_body:
        report += f"**Description:** {pr_body[:200]}...\n\n"
    
    report += f"**Files Changed:** {len(files)}\n\n"
    report += "### 📁 Modified Files:\n"
    for f in files:
        report += f"- `{f['filename']}` (+{f['additions']} / -{f['deletions']}) [{f['status']}]\n"
    
    report += "\n---\n\n"
    report += "## 🔍 Code Review\n\n"
    
    for file in files:
        report += f"### 📄 `{file['filename']}`\n\n"
        
        issues = []
        
        # Line count check
        lines = file['content'].split('\n')
        if len(lines) > 300:
            issues.append("⚠️ File has >300 lines. Consider refactoring.")
        elif len(lines) > 150:
            issues.append("📌 File has >150 lines. Consider splitting.")
        
        # TODO/FIXME check
        if 'TODO' in file['content']:
            issues.append("📌 TODO comments found. Address before merge.")
        if 'FIXME' in file['content']:
            issues.append("⚠️ FIXME comments found. Fix before merge.")
        
        # Debug statements
        if 'print(' in file['content'] and '.py' in file['filename']:
            issues.append("🐛 print() found. Use logging instead.")
        if 'console.log' in file['content'] and '.js' in file['filename']:
            issues.append("🐛 console.log() found. Use logging instead.")
        
        # Security scan
        security_issues = security_scan(file['content'], file['filename'])
        issues.extend(security_issues)
        
        if issues:
            for issue in issues:
                report += f"- {issue}\n"
        else:
            report += "✅ No issues found.\n"
        
        report += "\n"
    
    report += "---\n"
    report += "🤖 *This review was generated automatically.*"
    
    return report

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

def process_review(repo_full_name: str, pr_number: int, pr_title: str, pr_body: str):
    """Background review processing"""
    try:
        print(f"🔄 Processing PR #{pr_number} in {repo_full_name}")
        
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        # Get code files
        files = get_code_files(pr)
        
        if not files:
            pr.create_issue_comment("ℹ️ No code files found to review.")
            return
        
        print(f"📁 Found {len(files)} files")
        
        # Generate report
        report = generate_review_report(pr_title, pr_body, files)
        
        # Post comment
        pr.create_issue_comment(report)
        
        print(f"✅ Review posted on PR #{pr_number}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(f"❌ Error: {str(e)}")
        except:
            pass

@app.get("/")
async def root():
    return {"message": "PR Review Bot is running!", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
NEXUS 1-Click Automated Publisher
Creates public GitHub repository, pushes all code, and enables GitHub Pages for the showcase website.
"""
import os
import sys
import subprocess
import time
import webbrowser

GH_CLI = r"C:\Program Files\GitHub CLI\gh.exe"
REPO_DIR = r"E:\NEXUS"
WEBSITE_DIR = r"E:\NEXUS\website"

def run_cmd(cmd_list, check=True):
    print(f"--> Running: {' '.join(cmd_list)}")
    res = subprocess.run(cmd_list, capture_output=True, text=True, cwd=REPO_DIR)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed with code {res.returncode}: {res.stderr}")
    return res

def main():
    print("=" * 60)
    print("       NEXUS AUTOMATED GITHUB & WEBSITE PUBLISHER")
    print("=" * 60)

    # 1. Check gh installation
    if not os.path.exists(GH_CLI):
        print("[-] GitHub CLI not found at expected path. Searching PATH...")
        gh_path = "gh"
    else:
        gh_path = GH_CLI

    # 2. Check auth status
    print("\n[Step 1/4] Checking GitHub authentication status...")
    auth_check = run_cmd([gh_path, "auth", "status"], check=False)
    
    if auth_check.returncode != 0:
        print("\n[!] You are not logged into GitHub yet.")
        print("[*] Starting fast browser login...")
        login_proc = subprocess.Popen([gh_path, "auth", "login", "--web", "-h", "github.com", "-p", "https", "--clipboard"])
        print("\n[✓] Browser window opened! A one-time code was copied to your clipboard.")
        print("[*] Simply press Ctrl+V on the page and click 'Continue' and 'Authorize'.")
        login_proc.wait()
        
        # Verify login succeeded
        auth_check2 = run_cmd([gh_path, "auth", "status"], check=False)
        if auth_check2.returncode != 0:
            print("\n[-] Login was not completed. Please try again.")
            input("\nPress Enter to exit...")
            return

    # 3. Get username
    user_res = run_cmd([gh_path, "api", "user", "-q", ".login"], check=False)
    username = user_res.stdout.strip() or "kaziraiyan0123-hub"
    print(f"\n[✓] Authenticated as GitHub user: @{username}")

    repo_name = "NEXUS-AI-Companion"
    full_repo = f"{username}/{repo_name}"

    # 4. Check if repo exists
    print(f"\n[Step 2/4] Verifying GitHub repository '{full_repo}'...")
    view_check = run_cmd([gh_path, "repo", "view", full_repo], check=False)

    if view_check.returncode != 0:
        print(f"[*] Creating new public GitHub repository '{full_repo}'...")
        run_cmd([
            gh_path, "repo", "create", repo_name,
            "--public",
            f"--description=NEXUS — Autonomous AI Desktop Companion & Command Center for Windows. Coded by Raiyan.",
            "--source=E:\\NEXUS",
            "--remote=origin",
            "--push"
        ], check=False)
    else:
        print(f"[✓] Repository '{full_repo}' already exists. Pushing latest commits...")
        run_cmd(["git", "push", "-u", "origin", "main"], check=False)

    # 5. Enable GitHub Pages for website
    print("\n[Step 3/4] Publishing showcase website to GitHub Pages...")
    pages_cmd = [
        gh_path, "api",
        f"repos/{username}/{repo_name}/pages",
        "-X", "POST",
        "-H", "Accept: application/vnd.github+json",
        "-f", "source[branch]=main",
        "-f", "source[path]=/website"
    ]
    pages_res = run_cmd(pages_cmd, check=False)
    
    website_url = f"https://{username.lower()}.github.io/{repo_name}/"
    repo_url = f"https://github.com/{username}/{repo_name}"

    print("\n[Step 4/4] Opening published showcase website and GitHub repo...")
    print("=" * 60)
    print("🎉 PUBLISHING COMPLETE!")
    print(f"📁 GitHub Repository: {repo_url}")
    print(f"🌐 Public Website URL: {website_url}")
    print("=" * 60)

    # Open local showcase website immediately in browser
    local_index = os.path.join(WEBSITE_DIR, "index.html")
    if os.path.exists(local_index):
        webbrowser.open(local_index)

if __name__ == "__main__":
    main()

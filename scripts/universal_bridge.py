import json
import os
import sys
import subprocess
from github import Github


def main():
    if len(sys.argv) < 2:
        print("Usage: python universal_bridge.py <path_to_ai_json_output.json>")
        sys.exit(1)

    json_path = sys.argv[1]

    # 1. Read the AI's output
    print("🤖 Reading AI output...")
    with open(json_path, "r") as f:
        payload = json.load(f)

    commit_msg = payload.get("commit_message", "AI update")
    branch_name = payload.get("branch_name", "ai-update")
    files = payload.get("files", [])

    # 2. Write files to local disk
    print("Writing files to disk...")
    for file in files:
        path = file["path"]
        content = file["content"]

        # Create directories if needed
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

        with open(path, "w") as f:
            f.write(content)
        print(f"  -> Wrote {path}")

    # 3. Run the Fitness Function (Tests)
    print("🧪 Running fitness function (pytest)...")
    result = subprocess.run(["python3", "-m", "pytest", "-v"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Tests failed! The AI's code broke the kernel. Aborting commit.")
        print(result.stdout)
        sys.exit(1)

    print("✅ Tests passed!")

    # 4. Push to GitHub
    print("🚀 Pushing to GitHub...")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    g = Github(token)
    repo_name = os.environ.get("GITHUB_REPOSITORY", "Franksin2023/ai-os-seed")
    repo = g.get_repo(repo_name)

    # Create or get branch
    base_branch = repo.get_branch("main")
    try:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)
    except Exception:
        print(f"Branch {branch_name} already exists, updating it.")

    # Commit files
    for file in files:
        path = file["path"]
        content = file["content"]
        try:
            contents = repo.get_contents(path, ref=branch_name)
            repo.update_file(contents.path, commit_msg, content, contents.sha, branch=branch_name)
        except Exception:
            repo.create_file(path, commit_msg, content, branch=branch_name)

    print(f"🎉 Successfully pushed to branch: {branch_name}")
    print("You can now merge this branch on GitHub.")


if __name__ == "__main__":
    main()

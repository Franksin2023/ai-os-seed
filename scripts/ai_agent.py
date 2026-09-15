# scripts/ai_agent.py
import os
from openai import OpenAI
from github import Github

# Initialize APIs
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])

issue_title = os.environ['ISSUE_TITLE']
issue_body = os.environ['ISSUE_BODY']

print(f"🤖 AI Agent waking up for Issue: {issue_title}")

# 1. Ask the AI to write the code based on the issue
prompt = f"""
You are an expert Python developer working on the AI-OS-SEED project.
Read the GROWTH.md and SAFETY.md rules in the repo.

Here is the task you must complete:
Title: {issue_title}
Description: {issue_body}

Please write the exact Python code needed to solve this task.
Output ONLY the raw code, no markdown formatting.
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "system", "content": "You are a coding agent."},
              {"role": "user", "content": prompt}]
)

ai_code = response.choices[0].message.content

# 2. Save the code to the correct file
file_path = f"ai_os/agents/generated_{os.environ['ISSUE_NUMBER']}.py"

with open(file_path, "w") as f:
    f.write(ai_code)

print(f"✅ Code generated and saved to {file_path}")

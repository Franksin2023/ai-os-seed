# Universal AI Commit Protocol

When asked to modify the AI-OS-SEED repository, you MUST output your response as a single, valid JSON object. Do not include any conversational text outside the JSON.

The JSON must follow this exact schema:
```json
{
  "commit_message": "A brief description of the changes",
  "branch_name": "feature/your-branch-name",
  "files": [
    {
      "path": "path/to/file.py",
      "content": "The full, raw code for this file. Do not use markdown code blocks inside the JSON string. Escape all quotes and newlines properly."
    }
  ]
}
```

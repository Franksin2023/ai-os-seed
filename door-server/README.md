# Door Server (`door-server`)

`door-server` is a minimal Node.js/Express HTTP server that exposes a `POST /propose-change` endpoint to apply unified diffs to a local Git repository, run tests, and commit/push on success.

---

## 🛠 Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `REPO_PATH` | Path to local Git repository | Current working directory |
| `GIT_REMOTE` | Git remote name for pushing | `origin` |
| `DOOR_TOKEN` | Secret Bearer authentication token | Required |
| `TEST_COMMAND` | Command to run test suite | `npm test` or `make test` |
| `PORT` | Port for Express HTTP server | `3000` |

---

## 🚀 Installation & Running

```bash
cd door-server
npm install
REPO_PATH=/path/to/repo DOOR_TOKEN=yourtoken PORT=3000 node server.js
```

---

## 📡 Example Usage (`curl`)

```bash
curl -X POST http://localhost:3000/propose-change \
  -H "Authorization: Bearer yourtoken" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Add new memory optimization feature",
    "diff": "--- a/ai_os/kernel/memory.py\n+++ b/ai_os/kernel/memory.py\n@@ -10,1 +10,1 @@\n-# comment\n+# updated comment\n"
  }'
```

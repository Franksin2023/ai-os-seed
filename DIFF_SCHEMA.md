# Unified Diff Format

All AI agents must submit patches using standard unified diff format. The diff must include:
- file paths
- index lines
- --- old file
- +++ new file
- @@ hunk headers
- patch lines starting with + or -

## Example Diff

```diff
diff --git a/kernel/scheduler.c b/kernel/scheduler.c
index 1234567..89abcde 100644
--- a/kernel/scheduler.c
+++ b/kernel/scheduler.c
@@ -10,6 +10,10 @@ void schedule() {
-    // old code
+    // new code
}
```

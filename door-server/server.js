const express = require('express');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
const REPO_PATH = process.env.REPO_PATH || process.cwd();
const GIT_REMOTE = process.env.GIT_REMOTE || 'origin';
const DOOR_TOKEN = process.env.DOOR_TOKEN;

function getTestCommand() {
  if (process.env.TEST_COMMAND) {
    return process.env.TEST_COMMAND;
  }
  const pkgPath = path.join(REPO_PATH, 'package.json');
  if (fs.existsSync(pkgPath)) {
    return 'npm test';
  }
  return 'make test';
}

function runGit(args) {
  return execFileSync('git', args, { cwd: REPO_PATH, encoding: 'utf8' }).trim();
}

app.post('/propose-change', (req, res) => {
  // 1. Auth check
  const authHeader = req.headers['authorization'];
  if (!authHeader || !DOOR_TOKEN || authHeader !== `Bearer ${DOOR_TOKEN}`) {
    return res.status(401).json({ status: 'error', error: 'unauthorized' });
  }

  // 2. Body validation
  const { description, diff } = req.body;
  if (!description || typeof description !== 'string' || !description.trim()) {
    return res.status(400).json({ status: 'failed', error: 'Invalid or missing description' });
  }
  if (!diff || typeof diff !== 'string' || !diff.trim()) {
    return res.status(400).json({ status: 'failed', error: 'Invalid or missing diff' });
  }

  console.log(`[REQUEST] Incoming proposal: "${description}"`);

  // Timestamp for branch name: e.g. ai-change-20260915-193400
  const now = new Date();
  const dateStr = now.toISOString().replace(/[-T:]/g, '').slice(0, 14);
  const branchName = `ai-change-${dateStr}`;

  console.log(`[BRANCH] Creating and checking out branch: ${branchName}`);

  let originalBranch = 'main';
  try {
    originalBranch = runGit(['rev-parse', '--abbrev-ref', 'HEAD']);
  } catch (err) {
    console.warn('[GIT WARN] Could not determine HEAD branch:', err.message);
  }

  try {
    // Checkout new branch
    runGit(['checkout', '-b', branchName]);

    // Write diff to temp file and apply patch
    const patchFile = path.join(REPO_PATH, '.tmp_patch.diff');
    fs.writeFileSync(patchFile, diff);

    console.log('[PATCH] Applying unified diff...');
    try {
      execFileSync('patch', ['-p1', '-i', patchFile], { cwd: REPO_PATH });
      fs.unlinkSync(patchFile);
    } catch (patchErr) {
      if (fs.existsSync(patchFile)) fs.unlinkSync(patchFile);
      throw new Error(`Failed to apply patch: ${patchErr.message}`);
    }

    // Run tests
    const testCmd = getTestCommand();
    console.log(`[TEST] Running test command: "${testCmd}"`);
    try {
      const [cmd, ...cmdArgs] = testCmd.split(' ');
      execFileSync(cmd, cmdArgs, { cwd: REPO_PATH, stdio: 'inherit' });
      console.log('[TEST] Tests passed successfully.');
    } catch (testErr) {
      throw new Error(`Tests failed using command "${testCmd}"`);
    }

    // Run fitness evaluation engine
    console.log('[FITNESS] Running fitness evaluation engine...');
    try {
      execFileSync('bash', ['fitness/fitness_engine.sh', REPO_PATH, branchName], { cwd: REPO_PATH, stdio: 'inherit' });
      console.log('[FITNESS] Fitness evaluation passed successfully.');
    } catch (fitnessErr) {
      try {
        runGit(['reset', '--hard', 'HEAD']);
        runGit(['clean', '-fd']);
        runGit(['checkout', originalBranch]);
        runGit(['branch', '-D', branchName]);
      } catch (rollbackErr) {
        console.error(`[ROLLBACK ERROR] ${rollbackErr.message}`);
      }
      return res.status(400).json({
        status: 'failed',
        error: 'fitness score below threshold'
      });
    }

    // Commit and push
    console.log('[GIT] Committing changes...');
    runGit(['add', '-A']);
    runGit(['commit', '-m', `AI change: ${description}`]);

    console.log(`[GIT] Pushing to remote ${GIT_REMOTE}...`);
    runGit(['push', GIT_REMOTE, branchName]);

    console.log('[SUCCESS] Change proposed, tested, committed, and pushed!');
    return res.json({
      status: 'success',
      branch: branchName,
      description: description
    });

  } catch (err) {
    console.error(`[FAILURE] ${err.message}`);
    // Rollback
    try {
      runGit(['reset', '--hard', 'HEAD']);
      runGit(['clean', '-fd']);
      runGit(['checkout', originalBranch]);
      runGit(['branch', '-D', branchName]);
    } catch (rollbackErr) {
      console.error(`[ROLLBACK ERROR] ${rollbackErr.message}`);
    }

    return res.status(500).json({
      status: 'failed',
      error: err.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`[DOOR SERVER] Server listening on port ${PORT}`);
  console.log(`[DOOR SERVER] Target repo path: ${REPO_PATH}`);
  console.log(`[DOOR SERVER] Remote: ${GIT_REMOTE}`);
});

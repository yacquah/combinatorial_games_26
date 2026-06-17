# Contributing

This guide is for teammates who are new to Git. Follow these steps and you will avoid most merge conflicts and divergent branch problems.

## One-Time Setup

Clone the repository:

```bash
git clone https://github.com/yacquah/combinatorial_games_26.git
cd combinatorial_games_26
```

Tell Git to avoid accidental merge commits when pulling:

```bash
git config pull.rebase true
git config rebase.autoStash true
```

## Starting Work

Always start from a fresh `main`:

```bash
git switch main
git pull
git switch -c your-name/short-task-name
```

Good branch names:

```text
yaw/nim-mex-helper
jeffrey/chomp-start-logic
team/update-plan-notes
```

## Saving Work

Check what changed:

```bash
git status
```

Stage and commit:

```bash
git add path/to/file.py
git commit -m "Describe the change clearly"
```

Push your branch:

```bash
git push -u origin your-branch-name
```

Then open a pull request on GitHub.

## Before Opening a Pull Request

Update your branch with the latest `main`:

```bash
git fetch origin
git rebase origin/main
```

Run the basic Python check:

```bash
python3 -m compileall Nim Chomp nim_variant utils
```

Push after rebasing:

```bash
git push
```

If Git says the push was rejected after a rebase, use:

```bash
git push --force-with-lease
```

Only use `--force-with-lease` on your own feature branch. Never use it on `main`.

## Pull Request Rules

Each pull request should:

- Focus on one task.
- Explain what changed.
- Mention anything that still needs work.
- Pass the automated checks.
- Be reviewed before merging.

## Avoiding Merge Conflicts

Small pull requests are the best prevention.

- Pull from `main` before starting work.
- Rebase your branch often if others are merging changes.
- Avoid multiple people editing the same file at the same time.
- If a file is already being changed in another pull request, coordinate in the team chat first.

## If Something Goes Wrong

Do not panic and do not run random reset commands.

Run:

```bash
git status
```

Then ask for help and paste the output.

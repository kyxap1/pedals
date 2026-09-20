# Parallel sessions: shared files and git

Several sessions may convert different manuals in this checkout at once, so a
job touches only what its own slug keys — `<slug>/` and `_cctmp.<slug>/` — and
treats everything else in `git status` as a sibling's work in progress.

Four things are shared anyway: the root `index.html`, `catalog.txt`, this
skill's `SKILL.md` and `references/`.

## Editing a shared file

- Change them with small `Edit` calls only. `Write` rewrites the file from your
  copy and drops everyone else's hunks.
- Read right before editing; if `Edit` reports the file changed since it was
  read, re-read and redo the edit.
- Leave hunks you didn't write alone — no reverting, reformatting, reordering.

## Git, only when the user asks for a commit

- Stage your own paths by name and commit by path, so whatever another session
  staged stays out:

  ```
  git add <slug>/ && git commit -m "…" -- <slug>/ index.html catalog.txt
  ```

  Never `git add -A`, `git add .`, `git commit -a`, `git stash`.
- A shared file is committed whole. `git diff` it first; if it carries another
  session's hunk — a catalog card for a page that isn't published yet deploys
  as a broken link — ask the user before committing it.
- `.git/index.lock` exists → another session is mid-commit; wait and retry,
  never delete the lock.
- Push rejected because another session pushed first → tell the user; don't
  pull or rebase on your own.

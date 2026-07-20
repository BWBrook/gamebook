# Repository Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and publish a minimal, technology-neutral private repository for the gamebook project.

**Architecture:** Keep the repository documentation-first: three root-level repository files, two story-workspace readmes, and the design and implementation records. Consolidate the local setup into one root commit before creating and pushing the private GitHub remote.

**Tech Stack:** Git, GitHub CLI, Markdown, plain-text Git configuration files

## Global Constraints

- The repository remains technology-neutral.
- The default branch is `main`.
- The private GitHub remote is `BWBrook/gamebook`, connected as `origin` over SSH.
- The story roots are `stories/public_domain/howard/tower_of_the_elephant/` and `stories/original/`.
- Do not add a licence, runtime choice, dependency manifest, continuous integration configuration, source tree, test tree, or further domain-specific directories.
- Obtaining and converting *The Tower of the Elephant* is a later increment that must record source provenance and the rights basis.

---

## File map

- `README.md`: states the project's purpose, first playtest story, longer-term aim, and current planning status.
- `.gitignore`: excludes generic macOS, editor, and temporary files only.
- `.gitattributes`: normalises detected text files to LF line endings.
- `docs/superpowers/specs/2026-07-20-repository-skeleton-design.md`: records the approved design and acceptance criteria.
- `docs/superpowers/plans/2026-07-20-repository-skeleton.md`: records these implementation and verification steps.
- `stories/public_domain/howard/tower_of_the_elephant/README.md`: reserves the first adaptation workspace and lists provenance information required before importing source text.
- `stories/original/README.md`: reserves the original-story workspace without defining a format.

### Task 1: Create and consolidate the local repository skeleton

**Files:**

- Create: `README.md`
- Create: `.gitignore`
- Create: `.gitattributes`
- Create: `stories/public_domain/howard/tower_of_the_elephant/README.md`
- Create: `stories/original/README.md`
- Retain: `docs/superpowers/specs/2026-07-20-repository-skeleton-design.md`
- Retain: `docs/superpowers/plans/2026-07-20-repository-skeleton.md`

**Interfaces:**

- Consumes: the approved repository skeleton design.
- Produces: one clean local `main` commit containing exactly the seven planned files.

- [ ] **Step 1: Create the root project readme**

Create `README.md` with exactly:

```markdown
# Gamebook

A project to develop a streamlined gamebook system based on a cut-down version
of Barry W. Brook's full RPG ruleset.

The first adaptation and playtest will use Robert E. Howard's *The Tower of the
Elephant*. The longer-term aim is an expandable system for turning suitable
public-domain fiction into gamebooks, while also supporting original stories.

## Status

The repository is being established. The rules, implementation infrastructure,
and story-file formats have not yet been designed.

## Story workspaces

- `stories/public_domain/howard/tower_of_the_elephant/` — first adaptation and
  playtest.
- `stories/original/` — reserved for possible original works.

Source acquisition and conversion will be handled separately. Provenance and
the applicable rights basis will be recorded before source text is added.
```

- [ ] **Step 2: Create the generic Git configuration files**

Create `.gitignore` with exactly:

```gitignore
# macOS
.DS_Store
.AppleDouble
.LSOverride
._*

# Editors
*.swp
*.swo
*~
.idea/
.vscode/

# Temporary files
*.tmp
*.temp
```

Create `.gitattributes` with exactly:

```gitattributes
* text=auto eol=lf
```

- [ ] **Step 3: Create the tracked story-directory readmes**

Create `stories/public_domain/howard/tower_of_the_elephant/README.md` with exactly:

```markdown
# The Tower of the Elephant

This directory is reserved for the first gamebook adaptation and playtest,
based on Robert E. Howard's *The Tower of the Elephant*.

No source text has been imported. Before adding one, record its provider or
URL, edition or publication details, access date, applicable rights basis, and
any conversion notes.
```

Create `stories/original/README.md` with exactly:

```markdown
# Original stories

This directory is reserved for gamebooks based on original works. No story or
file format has yet been selected.
```

- [ ] **Step 4: Verify the proposed repository contents**

Run:

```bash
git diff --check
find . -path ./.git -prune -o -type f -print | sort
```

Expected file list:

```text
./.gitattributes
./.gitignore
./README.md
./docs/superpowers/plans/2026-07-20-repository-skeleton.md
./docs/superpowers/specs/2026-07-20-repository-skeleton-design.md
./stories/original/README.md
./stories/public_domain/howard/tower_of_the_elephant/README.md
```

Expected `git diff --check` result: no output and exit status 0.

- [ ] **Step 5: Consolidate the approved files into one initial commit**

Stage the exact file set:

```bash
git add .gitattributes .gitignore README.md \
  docs/superpowers/plans/2026-07-20-repository-skeleton.md \
  docs/superpowers/specs/2026-07-20-repository-skeleton-design.md \
  stories/original/README.md \
  stories/public_domain/howard/tower_of_the_elephant/README.md
```

Create a new root commit from the staged tree and move `main` to it using a
compare-and-swap update. The earlier local-only design commits remain
recoverable through Git's reflog.

```bash
gamebook_old_commit=$(git rev-parse HEAD)
gamebook_tree=$(git write-tree)
gamebook_new_commit=$(git commit-tree "$gamebook_tree" -m "chore: initialise repository")
git update-ref -m "consolidate initial repository history" \
  refs/heads/main "$gamebook_new_commit" "$gamebook_old_commit"
```

- [ ] **Step 6: Verify the consolidated local repository**

Run:

```bash
git status --short --branch
git rev-list --count HEAD
git log -1 --format=%s
git ls-tree -r --name-only HEAD | sort
```

Expected results:

- status is `## main` with no changes;
- commit count is `1`;
- commit subject is `chore: initialise repository`; and
- the tree contains exactly the seven paths listed in Step 4, without the leading `./`.

### Task 2: Create, push, and verify the private GitHub repository

**Files:** None.

**Interfaces:**

- Consumes: the clean one-commit local `main` branch from Task 1 and the authenticated `BWBrook` GitHub CLI session.
- Produces: private `BWBrook/gamebook`, configured as SSH remote `origin`, with local `main` tracking `origin/main` at the same commit.

- [ ] **Step 1: Perform the remote preflight checks**

Run:

```bash
gh auth status
gh repo view BWBrook/gamebook --json nameWithOwner,visibility,sshUrl
```

Expected results:

- `gh auth status` reports `BWBrook` as the active authenticated account with SSH Git operations;
- if `gh repo view` reports that the repository cannot be found, continue;
- if it returns a repository, stop and inspect its ownership, visibility, and contents rather than replacing or pushing over it.

- [ ] **Step 2: Create the private repository and push `main`**

Provided the preflight found no existing repository, run:

```bash
gh repo create BWBrook/gamebook --private --source=. --remote=origin --push
```

Expected result: GitHub creates `BWBrook/gamebook`, adds its SSH URL as `origin`, pushes `main`, and configures upstream tracking.

- [ ] **Step 3: Verify privacy, remote configuration, and commit parity**

Run:

```bash
git remote get-url origin
gh repo view BWBrook/gamebook \
  --json nameWithOwner,visibility,defaultBranchRef,sshUrl
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected results:

- remote URL is `git@github.com:BWBrook/gamebook.git`;
- repository is `BWBrook/gamebook` with visibility `PRIVATE` and default branch `main`;
- status is `## main...origin/main` with no changes; and
- `HEAD` and `origin/main` resolve to the same commit hash.


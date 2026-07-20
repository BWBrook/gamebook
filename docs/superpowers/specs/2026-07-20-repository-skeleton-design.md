# Repository Skeleton Design

## Purpose

Create a private, technology-neutral Git repository for developing a new
gamebook system. The system will first be developed and playtested by adapting
Robert E. Howard's *The Tower of the Elephant*, while leaving room for later
public-domain adaptations and original works.

The eventual rules will draw on a simplified version of Barry W. Brook's full
RPG ruleset and on lessons from gamebooks such as *Fighting Fantasy* and *Lone
Wolf*. Designing those rules, the adaptation workflow, and the implementation
infrastructure is outside this initial repository setup.

## Initial tracked files

The first published repository state will contain:

- `README.md`, describing the purpose, initial scope, and current planning
  status;
- `.gitignore`, excluding only generic macOS, editor, and temporary files;
- `.gitattributes`, normalising text-file line endings; and
- this design record;
- `docs/superpowers/plans/2026-07-20-repository-skeleton.md`, recording the
  implementation and verification sequence;
- `stories/public_domain/howard/tower_of_the_elephant/README.md`, reserving the
  workspace for the first adaptation; and
- `stories/original/README.md`, reserving a separate branch for possible
  original works.

The two story readmes will explain the purpose of their directories without
defining a source-text, adaptation, metadata, or build format. Empty directories
are not used because Git does not track them.

Obtaining a suitable public-domain source of *The Tower of the Elephant*,
recording its provenance and rights basis, and converting it to Markdown will
be a separate early increment.

It will not contain a licence, runtime choice, dependency manifest, continuous
integration configuration, source tree, test tree, or further domain-specific
directories. Those decisions belong to later planning increments.

## Git and GitHub setup

The local repository will use `main` as its default branch. Before the first
push, the approved design and skeleton files will be consolidated into one
initial commit named `chore: initialise repository`.

The remote will be a private GitHub repository at `BWBrook/gamebook`, connected
as `origin` over SSH. The initial branch will be pushed with upstream tracking.

## Verification

Setup is complete when:

1. the expected seven files are tracked and no unintended files are present;
2. the local working tree is clean on `main`;
3. `origin` points to the SSH URL for `BWBrook/gamebook`;
4. GitHub reports the repository as private; and
5. local `main` tracks `origin/main` at the same commit.

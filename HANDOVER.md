# Gamebook — successor handover

Prepared for Barry W. Brook on 7 September 2026. Start here; the old conversation
is not required. This is a current-state briefing, not a new design mandate.

## Start in the right checkout

Use `/Users/bwbrook/games/gamebook` on `main`. Barry explicitly requested a
consolidated, committed, pushed handover with only `main` remaining. The primer
rewrite and approved review edits have been integrated into `main`, including
commit `ef6a197`; this note is committed with the closeout. The former
`codex/reader-first-primer-rewrite` branch and its worktree are retired.

The current files on `main` are the revised text. There are no pending prose
edits from this task. Recheck `git status`, branches, worktrees, and remote
parity when starting; this snapshot can drift. Committing the draft does not
mean the remaining reader review is complete.

Below, `TOWER` means `stories/public_domain/howard/tower_of_the_elephant/`,
relative to the project root, not a required environment variable.

## Product and direction

Build a compact, paper-complete solo gamebook system derived from Barry's
*Sinew & Steel* RPG. The first adaptation is Howard's *The Tower of the
Elephant*, with a fixed young Conan. Later books may adapt other suitable
public-domain fiction or original stories. The authored book is authoritative;
any eventual digital companion remains optional.

Already present: source transcription and provenance, a whole-story adaptation
map, a story profile, a paper-playable outer-wall/garden slice, rules and sheet,
and a preliminary Python observer harness for physical-dice playtests. The
complete Tower adventure and a general digital engine are not finished.

The immediate work is **awaiting reader review**. An earlier calibration exposed
a primer written too much like an internal specification. The approved rewrite
introduces the story and Conan, then teaches through concrete situations in
plain prose. It should work for a capable twelve-year-old without patronising
adult readers or assuming knowledge of Howard, gamebooks, or the parent RPG.

## Exact review position and next action

Barry wants to review **one or two subsections at a time**, with the actual prose
shown in the conversation and time to respond. Continue that cadence; this is
a requested editorial collaboration, not an unnecessary approval ladder.

- The opening and earlier Part I text have been reviewed. Most recently Barry
  explicitly approved the merged **Fortune** passage and revised **Natural
  Results** passage. Advantage and Disadvantage was already approved.
- The last response presented **Stamina, Possessions, and Story Marks** and
  **Tactical Exchanges and Endings**, which finish Part I. Barry has **not yet
  given feedback on these two**; he requested this handover instead.
- Resume by presenting those two current subsections for feedback, unless Barry
  supplies acceptance or edits in his opening prompt. Do not silently mark them
  approved. Then progress through Part II: **Conan and His Starting Sheet**,
  **Exposure**, **Injury, Recovery, and Action**, **Rumours of the Tower**;
  then **Rules at a Glance** and the **Adventure Sheet**.

Accepted wording choices include “records” for the Adventure Sheet, “Choices
might also prescribe other conditions”, Fortune as “Conan's luck in a tight
corner”, and “low is good, because this is a roll-under system”. The separate
worked-example subsection was removed: the courtyard climb now teaches Fortune,
and Natural Results briefly revisits it. Avoid reintroducing duplication.

Barry prefers to bundle editorial edits rather than commit each small change.
His final closeout request authorized committing, merging, and pushing the
current bundle and removing the redundant branch and worktree; that supersedes
the earlier instruction to leave this bundle uncommitted. It does not approve
the unread primer sections. Finish the primer and sheet review before live calibration;
show S01 only after Barry explicitly says he is ready. Do not start a playtest
merely because its command appears in a document.

## Read selectively

First read `TOWER/playtest/quick-rules.md` and `adventure-sheet.md`. For rationale, use
`docs/superpowers/specs/2026-08-01-reader-first-player-primer-rewrite-design.md`.
Its presentation requirements supersede the July primer design; subsequent
user-approved edits supersede its original example layout.

As needed:

- `docs/superpowers/specs/2026-07-30-authored-sinew-steel-solo-core-design.md`:
  settled core direction; some original status prose predates implementation.
- `TOWER/adaptation/story-profile.md`: exact Tower mechanics and slice limits.
- `TOWER/adaptation/map.md`, `source.md`, and `README.md`: source fidelity and
  provenance. Preserve the source and its jurisdiction-specific rights record.
- `docs/playtesting/live-playtest.md`: observer protocol and future
  `tower-calibration-03` setup. Earlier calibration evidence stays local;
  the paused `tower-calibration-02` must not resume against rewritten files.

The Git-ignored `.playtest/sessions/` in the main checkout retains calibration
01 and 02 evidence. These records are intentional local data, not disposable
worktree residue. Old `.superpowers` preview material was moved to macOS Trash
during cleanup; it is not needed to resume this project.

Avoid loading every historical plan or unread story passage just to bootstrap.
The root README understates the now-existing observer tooling; inspect current
files when a status statement conflicts with implemented work.

## Contracts and evidence

Keep the settled mechanics: d20 roll-under; target minus die gives Margin;
Advantage keeps the lower die, Disadvantage the higher; natural 1/20 are locked;
ordinary Fortune expenditure lowers the die, and a Fortune test fixes its
target before spending. Tactical exchanges use authored methods and consequences.
There are no opponent rolls or repeated combat rounds. Exposure 3/4 means
unease/search, with restrictions only where a passage specifies them.

The four H2 primer sections and rules-then-sheet links are harness contracts.
Numbered story text from S01 onward is protected during this rewrite.
`tests/test_player_primer.py` checks all three boundaries, including the story
digest. At closeout, these passed against the revised files:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
git diff --check
```

Result: all 72 tests passed; no whitespace errors. Use proportionate checks after further edits;
for changes to the observer itself, also run its relevant tests. Passing these
checks does not substitute for Barry's assessment of the prose or actual play.

## Skills and working style

Read the installed skills when applying them:

- [Twilight Laboratory](/Users/bwbrook/.codex/skills/twilight-laboratory/SKILL.md):
  recover the operating state, carry forward authorization, and complete coherent
  tranches. Here the valuable human decision is reader experience; preserve the
  explicitly requested small review chunks.
- [Kill Your Darlings](/Users/bwbrook/.codex/skills/kill-your-darlings/SKILL.md):
  keep only complexity serving the current book and meaningful verification.
  Use it to resist redundant explanation and premature engine development;
  its invocation does not authorize unrelated deletion or a fresh broad audit.
- [Audit AI Writing](/Users/bwbrook/.codex/skills/audit-ai-writing/SKILL.md):
  useful for substantive prose edits, preserving voice, concrete verbs, and
  examples while removing generic AI phrasing. Do not polish accepted text
  merely to exercise a new model.

The next milestone is an accepted primer and usable sheet, followed by a fresh
reader-led calibration of the existing slice. Let that evidence guide further
adaptation and tooling. Bring independent judgment, but reopen settled choices
only for a concrete problem or a new direction from Barry.

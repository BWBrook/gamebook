# *The Tower of the Elephant* Source Markdown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a faithful, provenance-backed Markdown source of Robert E. Howard's *The Tower of the Elephant* to its story workspace.

**Architecture:** Freeze the selected Project Gutenberg Australia HTML response by checksum, convert only its three narrative chapters to Markdown, and make six secondary-source-confirmed hyphen repairs. Keep the narrative in `source.md` and the source, conversion, and rights record in the adjacent `README.md`.

**Tech Stack:** `curl`, Pandoc 3.10, POSIX text tools, Git, Markdown

## Global Constraints

- Import the source story only; do not analyse, abridge, adapt, annotate, or divide it into gamebook passages.
- Use Project Gutenberg Australia eBook `0600831h.html`, March 2020, as the base text.
- Use Wikisource only to check mechanical transcription artefacts, not to silently replace the base edition.
- Preserve story wording and paragraph order.
- Remove source-site navigation, licence boilerplate, images, captions, table of contents, promotional material, horizontal section separators, and `THE END` display furniture.
- Do not modernise spelling, punctuation, diction, or historical language.
- Record observation separately from the project's rights inference; do not present the assessment as legal advice.

---

## File map

- `stories/public_domain/howard/tower_of_the_elephant/source.md`: title, author, three chapter headings, and complete narrative.
- `stories/public_domain/howard/tower_of_the_elephant/README.md`: source identity, checksum, conversion record, rights evidence, and scope boundary.
- `docs/superpowers/specs/2026-07-20-tower-source-markdown-design.md`: approved design and acceptance criteria.
- `docs/superpowers/plans/2026-07-20-tower-source-markdown.md`: implementation and verification sequence.

### Task 1: Freeze and convert the source text

**Files:**

- Create: `stories/public_domain/howard/tower_of_the_elephant/source.md`
- Retain: `docs/superpowers/specs/2026-07-20-tower-source-markdown-design.md`
- Retain: `docs/superpowers/plans/2026-07-20-tower-source-markdown.md`

**Interfaces:**

- Consumes: Project Gutenberg Australia HTML at `https://gutenberg.net.au/ebooks06/0600831h.html`.
- Produces: a source Markdown file whose narrative is mechanically traceable to SHA-256 `c2d762385e8453de2c58c0d1ddcb9a0f170f24263935c64487213d893998dfba`.

- [ ] **Step 1: Check the conversion tools**

Run:

```bash
command -v curl
command -v pandoc
command -v shasum
pandoc --version | sed -n '1,3p'
```

Expected: all three commands resolve, and Pandoc reports version 3.10.

- [ ] **Step 2: Download and freeze the base HTML in temporary storage**

Run:

```bash
gamebook_source_tmp=$(mktemp -d /tmp/gamebook-tower-source.XXXXXX)
curl -L --fail --silent --show-error \
  https://gutenberg.net.au/ebooks06/0600831h.html \
  -o "$gamebook_source_tmp/0600831h.html"
shasum -a 256 "$gamebook_source_tmp/0600831h.html"
```

Expected checksum:

```text
c2d762385e8453de2c58c0d1ddcb9a0f170f24263935c64487213d893998dfba
```

Stop if the checksum differs, because a changed upstream response requires a
fresh textual review and provenance update.

- [ ] **Step 3: Convert the HTML and isolate the narrative**

Run:

```bash
pandoc --from=html --to=gfm --wrap=none \
  "$gamebook_source_tmp/0600831h.html" \
  -o "$gamebook_source_tmp/full.md"

{
  printf '# The Tower of the Elephant\n\n*Robert E. Howard*\n\n'
  awk '
    /^## <span id="tower1">CHAPTER 1<\/span>$/ { in_story = 1 }
    in_story && /^## THE END$/ { exit }
    in_story && /^-{10,}$/ { next }
    in_story { print }
  ' "$gamebook_source_tmp/full.md"
} | perl -pe '
  s/^## <span id="tower1">CHAPTER 1<\/span>$/## Chapter 1/;
  s/^## <span id="tower2">CHAPTER 2<\/span>$/## Chapter 2/;
  s/^## <span id="tower3">CHAPTER 3<\/span>$/## Chapter 3/;
  s/([[:alpha:]])- ([[:alpha:]])/$1-$2/g;
' | perl -0pe 's/\n+\z/\n/' \
  > stories/public_domain/howard/tower_of_the_elephant/source.md
```

This deliberately repairs the six observed spacing artefacts:
`smoke-stained`, `quick-fingered`, `bold-eyed`, `high-strapped`,
`death-stroke`, and `bull-neck`.

- [ ] **Step 4: Confirm the six repairs against Wikisource**

Run:

```bash
for gamebook_chapter in I II III; do
  curl -L --fail --silent --show-error \
    "https://en.wikisource.org/wiki/The_Tower_of_the_Elephant/Chapter_${gamebook_chapter}?action=render" \
    -o "$gamebook_source_tmp/wikisource-${gamebook_chapter}.html"
done

pandoc --from=html --to=plain --wrap=none \
  "$gamebook_source_tmp"/wikisource-*.html \
  -o "$gamebook_source_tmp/wikisource.txt"

rg -o 'smoke-stained|quick-fingered|bold-eyed|high-strapped|death-stroke|bull-neck' \
  "$gamebook_source_tmp/wikisource.txt" | sort -u
```

Expected: all six repaired forms appear once in the sorted unique output.

- [ ] **Step 5: Verify narrative fidelity against the normalised base extraction**

Create the comparison file using the same bounded extraction and mechanical
normalisations:

```bash
awk '
  /^## <span id="tower1">CHAPTER 1<\/span>$/ { in_story = 1 }
  in_story && /^## THE END$/ { exit }
  in_story && /^-{10,}$/ { next }
  in_story { print }
' "$gamebook_source_tmp/full.md" | perl -pe '
  s/^## <span id="tower1">CHAPTER 1<\/span>$/## Chapter 1/;
  s/^## <span id="tower2">CHAPTER 2<\/span>$/## Chapter 2/;
  s/^## <span id="tower3">CHAPTER 3<\/span>$/## Chapter 3/;
  s/([[:alpha:]])- ([[:alpha:]])/$1-$2/g;
' | perl -0pe 's/\n+\z/\n/' \
  > "$gamebook_source_tmp/expected-narrative.md"

awk '/^## Chapter 1$/ { in_story = 1 } in_story { print }' \
  stories/public_domain/howard/tower_of_the_elephant/source.md \
  > "$gamebook_source_tmp/actual-narrative.md"

diff -u \
  "$gamebook_source_tmp/expected-narrative.md" \
  "$gamebook_source_tmp/actual-narrative.md"
```

Expected: `diff` produces no output and exits 0.

- [ ] **Step 6: Run structural and contamination checks**

Run:

```bash
rg -n '^# ' stories/public_domain/howard/tower_of_the_elephant/source.md
rg -n '^## Chapter [123]$' stories/public_domain/howard/tower_of_the_elephant/source.md
rg -n '^(TORCHES flared|Into the waving green gardens)' \
  stories/public_domain/howard/tower_of_the_elephant/source.md
rg -n '<[^>]+>|Project Gutenberg|TABLE OF CONTENTS|THE END|!\[|^-{10,}$' \
  stories/public_domain/howard/tower_of_the_elephant/source.md
LC_ALL=C rg -n $'\xEF\xBF\xBD|\xC2\xAD' \
  stories/public_domain/howard/tower_of_the_elephant/source.md
git diff --check
```

Expected:

- one title at line 1;
- exactly three chapter headings in order;
- the first and final narrative paragraphs are found;
- the contamination and replacement/soft-hyphen searches return no matches;
- `git diff --check` returns no output; and
- the Markdown contains between 8,000 and 12,000 words.

### Task 2: Record provenance, validate the increment, and publish it

**Files:**

- Modify: `stories/public_domain/howard/tower_of_the_elephant/README.md`
- Create: `stories/public_domain/howard/tower_of_the_elephant/source.md`
- Create: `docs/superpowers/plans/2026-07-20-tower-source-markdown.md`
- Retain: `docs/superpowers/specs/2026-07-20-tower-source-markdown-design.md`

**Interfaces:**

- Consumes: the verified `source.md` and the rights/source research listed below.
- Produces: a documented, committed, and pushed source increment on `main`.

- [ ] **Step 1: Replace the story readme with the provenance record**

Use `apply_patch` to replace the existing readme with:

```markdown
# The Tower of the Elephant

This directory contains the source text for the first gamebook adaptation and
playtest, based on Robert E. Howard's *The Tower of the Elephant*.

## Source edition

- Author: Robert E. Howard (1906-1936)
- First publication: *Weird Tales*, March 1933
- Base transcription: Project Gutenberg Australia, eBook `0600831h.html`
- PGA edition: first posted May 2006; updated March 2020
- PGA producers: Richard Scott, Colin Choat, Matthias Kaether, and Roy Glashan
- Source URL: <https://gutenberg.net.au/ebooks06/0600831h.html>
- Retrieved: 20 July 2026
- Downloaded HTML SHA-256: `c2d762385e8453de2c58c0d1ddcb9a0f170f24263935c64487213d893998dfba`
- Secondary text check: <https://en.wikisource.org/wiki/The_Tower_of_the_Elephant>

The converted text is in [`source.md`](source.md). It preserves the PGA
narrative and paragraph order while removing website material and images.

## Conversion record

Pandoc 3.10 converted the HTML to GitHub-flavoured Markdown. The conversion
retains the title, author, and three narrative chapters. It omits PGA
navigation, licence boilerplate, cover and interior images, captions, table of
contents, promotional footer, and the `THE END` display heading.
Horizontal separators used as source-page furniture are also omitted.

Six spaces introduced inside hyphenated words were removed after comparison
with Wikisource: `smoke-stained`, `quick-fingered`, `bold-eyed`,
`high-strapped`, `death-stroke`, and `bull-neck`. No other wording,
punctuation, spelling, or paragraph changes were made. No unresolved textual
differences remain from this mechanical conversion review.

## Rights assessment

The project treats this story text as public domain in Australia and the United
States based on the records below. This is a documented project assessment,
not legal advice.

Observed evidence:

- Howard died on 11 June 1936, according to the
  [Handbook of Texas](https://www.tshaonline.org/handbook/entries/howard-robert-ervin).
- The story was published during his lifetime in March 1933.
- The [Australian Government copyright-term table](https://www.infrastructure.gov.au/sites/default/files/fact_sheet_copyright_terms_0.pdf)
  says copyright has expired for a literary work made public before the
  author's death when the author died before 1 January 1955. Its transition
  note says the 2005 term extension did not revive copyright that had already
  expired.
- The [National Library of Australia](https://www.library.gov.au/services/copyright-library-collections/how-long-does-copyright-last)
  likewise states that published works whose creators died before 1 January
  1955 are generally in the Australian public domain.
- [Project Gutenberg Australia](https://gutenberg.net.au/ebooks06/0600831h.html)
  identifies this ebook as produced from a printed edition in the Australian
  public domain. Its [licence](https://gutenberg.net.au/licence.html) permits
  reuse subject to national law and requires PGA branding and added material
  to be removed from modified copies; neither is included in `source.md`.
- The University of Pennsylvania's
  [*Weird Tales* renewal index](https://onlinebooks.library.upenn.edu/webbin/cinfo/weirdtales)
  lists the March 1933 issue renewal separately from renewed individual
  contributions. *The Tower of the Elephant* does not appear in its list of
  renewed contributions.
- [Wikisource](https://en.wikisource.org/wiki/The_Tower_of_the_Elephant)
  classifies the story as public domain in the United States because no
  contribution renewal was found.

Project inference: the work had entered the Australian public domain before
the 2005 term extension, and the available US renewal records do not show a
renewal for Howard's individual contribution. The renewed copyright in the
March 1933 magazine issue is therefore recorded separately and is not treated
as a renewal of this story.

All online records above were accessed on 20 July 2026.

## Scope

`source.md` is the reference text for later analysis and adaptation. It is not
yet divided into gamebook passages and contains no rules, annotations, or
adapted prose.
```

- [ ] **Step 2: Run the complete acceptance checks**

Run:

```bash
git diff --check
test "$(rg -c '^# The Tower of the Elephant$' stories/public_domain/howard/tower_of_the_elephant/source.md)" -eq 1
test "$(rg -c '^## Chapter [123]$' stories/public_domain/howard/tower_of_the_elephant/source.md)" -eq 3
test "$(wc -w < stories/public_domain/howard/tower_of_the_elephant/source.md)" -ge 8000
test "$(wc -w < stories/public_domain/howard/tower_of_the_elephant/source.md)" -le 12000
perl -0ne 'exit 1 if /\n\n\z/' stories/public_domain/howard/tower_of_the_elephant/source.md
test -z "$(git grep -n -E '<[^>]+>|Project Gutenberg|TABLE OF CONTENTS|THE END|!\[|^-{10,}$' -- stories/public_domain/howard/tower_of_the_elephant/source.md || true)"
git status --short
```

Expected: every assertion exits 0; the diff check is silent; status shows only
the modified design and story readme, plus the untracked plan and `source.md`.

- [ ] **Step 3: Commit and push the increment**

Run:

```bash
git add \
  docs/superpowers/specs/2026-07-20-tower-source-markdown-design.md \
  docs/superpowers/plans/2026-07-20-tower-source-markdown.md \
  stories/public_domain/howard/tower_of_the_elephant/README.md \
  stories/public_domain/howard/tower_of_the_elephant/source.md
git commit -m "feat: add Tower of the Elephant source text"
git push origin main
```

Expected: one feature commit is created and pushed to `origin/main`.

- [ ] **Step 4: Verify repository and remote parity**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git log -2 --oneline --decorate
```

Expected: the working tree is clean; `main` tracks `origin/main`; both commit
hashes match; and the newest commit subject is
`feat: add Tower of the Elephant source text`.

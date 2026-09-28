# Local reader — approved implementation tranche

Barry approved the local browser reader on 20 September 2026. Status: closed;
implementation and interface checks complete, awaiting Barry's actual playtest.
Twilight Laboratory is the working cadence, adapted to game/book development.

## Completion boundary

Deliver the complete accepted S01–S14/E01–E03 slice in a readable local browser
interface with explicit legal choices, physical-dice entry, Fortune decisions,
automatic sheet updates, saved progress, reached-passage review, quoted and
passage-level notes, and a downloadable session report. Browser-check the actual
flow, including reload/resume and feedback persistence. Leave it ready for Barry
to begin a fresh playthrough on this MacBook.

Keep the authored Markdown and mechanics unchanged. In particular every kept
natural 20 at the lion is lethal. No AI calls, hosting, publication, automatic
play, new adventure passages, or changes to old calibration records are included.
No commit or push is part of this tranche.

## Implementation and evidence

- Python serves a small local reader on loopback and persists sessions beneath
  the existing ignored `.playtest/` directory. The interface uses local assets.
- A slice-specific deterministic engine explicitly maps choices and outcomes;
  it reuses the existing dice/Fortune functions. Validate the source fingerprint
  before starting a session so prose changes cannot silently outgrow the mapping.
- Sessions snapshot the reader text. Rolls, actions and notes retain revision
  and state context. Reading an old passage does not rewind play.
- Persist each successful operation atomically; reject stale browser mutations.
  A changed engine requires a new playthrough; old sessions remain reviewable.
- Test consequential branches, invalid requests, saved-state integrity and quote
  anchoring. Browser checks establish interface function, not literary quality,
  player fairness or print usability.

## Visual direction

Quiet three-column book reader: navy sheet rail, cool near-white reading page,
serif prose, restrained gold accents and a margin for notes. On smaller screens,
secondary panels collapse while text stays readable. No product illustrations
are needed. One generated concept informs the layout; its invented prose and
incorrect example dice controls are explicitly discarded in favour of the
authoritative manuscript and approved d20 rules. The result panel appears only
when a real action reaches it.

## Responsibilities

Astra owns integration, HTTP/persistence, verification and handoff. Bounded
worker assignments cover the slice engine/tests and the static reading UI.
Fable's advisory budget is reserved for substantive design questions after
actual reader feedback, rather than a parallel implementation review.

## Acceptance evidence — 20 September

- All 89 unittest checks pass, including the existing observer/primer suite,
  explicit engine branches, snapshot/quote integrity, atomic save failure,
  stale-tab rejection and HTTP boundaries. JavaScript syntax and whitespace
  checks pass. The authoritative story, primer, profile and sheet are unchanged.
- Codex in-app browser completed S01 → S03 → S04 → S05 → S06 → S07 → S08 →
  S09 → S10 → S11 → S12 → S14. Cunning 15 spent 3 Fortune; spear dice 6/20
  kept 6, consumed the spear and finished at Fortune 7 / Stamina 6 / Exposure 0.
- A separate browser attempt used evasive lion natural 20 and reached E03
  without a Fortune prompt. These were disposable test readings, not Barry's
  play evidence, and were kept out of his session directory.
- Quoted S01 feedback and a rules note persisted across browser/server-store
  reload. The saved JSON independently matched the visible result. Journey
  review retained the current sheet. A draft survived page reload on mobile.
- Visual inspection used the in-app browser at its normal laptop width, the
  concept's native 1505 × 1045 dimensions, and 390 × 844. At the narrow width,
  36px body text produced no horizontal overflow. Temporary viewport overrides
  were reset at handoff.

### Focused visual review

The generated concept was inspected alongside browser screenshots using
`view_image`. The final interface follows its navy/cool-white/gold palette,
serif hierarchy, three-column reading/sheet/notes layout, modest bordered
controls and restrained spacing. The actual body copy is verified as 21px,
normal weight; controls remain code-native. The quoted-note composer and margin
markers are functional rather than mock data.

Intentional differences: the real primer precedes S01; full authoritative choice
instructions remain visible above action buttons; invented concept prose and
incorrect dice examples are excluded; results appear only at their proper phase;
the rails collapse responsively. Additional above-the-fold copy is limited to
reader onboarding, save state and feedback instructions. No decorative imagery
or external assets are used. These differences implement the approved functional
requirements rather than extending the adventure.

Repairs from the browser pass: keep header/sheet/notes reachable while scrolling,
focus same-passage dice/Fortune controls instead of jumping back to the heading,
provide a Begin action after the rules, and preserve whitespace/ignore note icons
when selecting a quotation. No known blocking functional or layout defect remains.

The local server is left running at http://127.0.0.1:8767 with no user reading
started. Launch again with `Play Tower.command` when needed. No commit, push or
hosting deployment was performed. Reader judgement and print usability remain
untested by this implementation tranche.

## Review pass — 28 September

At Barry's request, Fable played two QA routes in a separate sessions directory
before his first reading and repaired four defects: triple-clicking a passage's
last paragraph could not start a note; the primer could not be annotated on
first read, so a new reading now opens on the rules; the result panel showed
engine-written paraphrase, so it now quotes the authored result paragraph for
the chosen method and outcome; and one unreadable session file hid every
reading. Smaller changes: S13 names its destination, Exposure-costing choices
show their cost, Charter replaces Georgia for lining figures, the cursor lands
in the die field, Fortune offers one-click choices, Cmd-Enter saves a note, and
the report leads with notes. 94 tests pass. Discussion 47 on the board records
the details and the points deferred until after Barry's reading. The tranche
was committed and pushed on Barry's instruction; Barry's reading directory was
empty at commit time.

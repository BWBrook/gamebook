# Local browser playtest

The browser reader plays the accepted outer-wall/garden slice, ending at the
secured rope or one of the three alternate endings. It preserves the authored
Markdown and uses an explicit, tested mapping for the current choices and rules.

## Open the reader

Double-click **Play Tower.command** in the project folder. Keep its terminal
window open while reading. Alternatively, from the repository root:

```sh
uv run python -m tools.reader_server --open
```

Open <http://127.0.0.1:8767>. The server listens only on this MacBook's loopback
interface. It uses no model API, external fonts or hosted service. The first
`uv run` installs the one rendering dependency; subsequent reading can work
offline. Stop the server with Ctrl-C; saved readings remain available next time.

## Play and annotate

Name the reading if useful and choose **Begin a reading**. The reading opens on
the rules, where notes already work; choose **Begin at S01** when ready.
Use the printed actions beneath each passage. For a test, choose the method,
roll physical d20s, and type the faces shown; the cursor waits in the die field.
With Advantage, enter both dice; the reader keeps the lower. On an ordinary
roll, choose **Spend N Fortune and succeed**, keep the roll, or enter another
amount. A kept natural 1 or 20 cannot be changed. All lion methods retain
Barry's chosen natural-20 lethality. The result panel quotes the book's own
printed result line for the method and outcome; the reader writes no story
prose of its own.

The sheet changes as instructions resolve. Costs are applied once; **Continue**
after a result takes you to its destination. Completed readings remain available
for review and notes. **New reading** starts a separate attempt rather than
overwriting the previous one.

Highlight a phrase in the passage to attach a quotation to a note, or type a
note without highlighting for passage-level feedback. Triple-clicking a
paragraph works; Cmd-Enter saves the note. Saved notes retain the
text revision, quotation, passage, time, and current game state. The **Rules**
view also accepts notes in an existing reading. Drafts are retained locally in
the browser; press **Save note** to include a note in the durable session file
and report.

**Journey** revisits only reached passages. Reviewing an earlier passage does
not rewind the sheet or replay consequences. Return to the current passage to
continue play. **Download reading report** exports a Markdown account that
leads with the notes, grouped by passage in the order reached, followed by a
one-row-per-step table of actions, dice, Fortune decisions and sheet changes.
The session JSON remains the complete machine record.

## Where the evidence lives

Browser sessions are individual JSON files in `.playtest/browser-sessions/`,
ignored by Git. They are separate from the earlier observer calibrations in
`.playtest/sessions/`. Each file contains a snapshot of its reader text, current
state, recorded actions and notes. Each successful operation is saved atomically.
Conflicting requests from another tab are rejected rather than replayed.

When Barry returns to Codex, Astra can inspect these files and report the
feedback. No background AI watches the reading, and notes are not automatically
posted to the correspondence board. Curated questions can be taken to Fable
within Barry's agreed collaboration scope.

An older session continues to display the text it began with. If the engine
implementation changes, that session becomes review-only, with notes and export
still available. Starting against edited passage text requires reviewing the
explicit mechanics mapping and updating its content fingerprint. Do not merely
change the fingerprint to silence a mismatch.

## Development and verification

```sh
uv run python -B -m unittest discover -s tests
git diff --check
```

Use a different port and temporary session directory for interface checks, for
example `--port 8768 --sessions-dir .playtest/browser-qa`. Never exercise tests
inside Barry's live readings. Browser verification establishes interface and
bookkeeping behaviour; it does not establish literary quality, fairness,
balanced routes or paper usability.

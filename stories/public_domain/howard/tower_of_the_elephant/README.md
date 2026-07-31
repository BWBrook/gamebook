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
contents, promotional footer, horizontal section separators, and the `THE END`
display heading.

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

## Adaptation work

- [`adaptation/map.md`](adaptation/map.md) maps the complete source into
  invariants, decision seams, elastic intervals, and counterfactual boundaries.
- [`adaptation/story-profile.md`](adaptation/story-profile.md) fixes Conan's
  profile, Exposure, sparse state, and the first passage graph.
- [`playtest/quick-rules.md`](playtest/quick-rules.md) contains the reader-facing
  rules for the representative slice.
- [`playtest/adventure-sheet.md`](playtest/adventure-sheet.md) is the paper
  record sheet.
- [`playtest/slice-01.md`](playtest/slice-01.md) is the playable outer-wall and
  garden slice.
- [`playtest/slice-01-audit.md`](playtest/slice-01-audit.md) records source and
  state coverage, deterministic route rehearsals, and the reader-only procedure
  run.

The slice is a development playtest through the secured-rope boundary at source
line 188. It is not a complete adaptation of *The Tower of the Elephant*.

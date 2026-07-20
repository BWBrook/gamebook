# *The Tower of the Elephant* Source Markdown Design

## Goal

Create a faithful, readable Markdown transcription of Robert E. Howard's *The
Tower of the Elephant* for the first gamebook adaptation workspace. Record
enough provenance and rights evidence for another contributor to identify the
source edition, reproduce the conversion, and understand why the text is being
treated as public domain.

This increment imports the source story only. It does not analyse, abridge,
adapt, annotate, or divide the story into gamebook passages.

## Source selection

The base text will be the March 2020 Project Gutenberg Australia HTML edition:

- <https://gutenberg.net.au/ebooks06/0600831h.html>
- eBook number `0600831h.html`
- first posted May 2006 and most recently updated March 2020
- produced by Richard Scott, Colin Choat, Matthias Kaether, and Roy Glashan

This edition is selected because it is complete, cleanly structured into the
story's three chapters, and explicitly identifies its production history and
Australian public-domain basis.

The Wikisource transcription will be used as a secondary comparison source:

- <https://en.wikisource.org/wiki/The_Tower_of_the_Elephant>

It will resolve obvious conversion artefacts such as soft hyphens or spaces
introduced within hyphenated words. It will not silently replace the selected
base edition.

## Rights and provenance record

The story readme will record observation separately from inference:

- observed first publication in *Weird Tales*, March 1933;
- observed author death in 1936;
- Project Gutenberg Australia's statement that its edition was made from
  printed material in the Australian public domain;
- the Australian Government and National Library rules that a literary work
  made public during its author's lifetime is out of copyright in Australia if
  the author died before 1 January 1955, and that the 2005 term extension did
  not revive expired copyright;
- the University of Pennsylvania renewal index's separate lists of renewed
  *Weird Tales* issues and renewed individual contributions, with this story
  absent from the contribution-renewal list; and
- Wikisource's classification of the story as public domain in the United
  States for lack of a contribution renewal.

The readme will link to each online record, include the access date, and store
the SHA-256 checksum of the exact downloaded Project Gutenberg Australia HTML.
It will describe the rights conclusion as a documented project assessment,
not legal advice.

## Markdown conversion

Create:

`stories/public_domain/howard/tower_of_the_elephant/source.md`

The file will contain:

1. `# The Tower of the Elephant`;
2. `Robert E. Howard` in italics;
3. `## Chapter 1`, `## Chapter 2`, and `## Chapter 3`; and
4. the complete story text beneath those headings.

Remove Project Gutenberg Australia navigation, licence boilerplate, cover and
interior images, captions, table of contents, promotional footer, and `THE END`
display furniture, including its horizontal section separators. The story's
wording and paragraph order remain unchanged.

Mechanical normalisation is limited to:

- converting HTML structure to GitHub-flavoured Markdown;
- normalising line endings and whitespace;
- removing soft-hyphen characters;
- repairing spaces inserted inside clearly hyphenated words when confirmed by
  the secondary source; and
- using consistent Arabic chapter numbers in headings.

No spelling, punctuation, diction, or historical language will be modernised.
Any substantive discrepancy that cannot be resolved mechanically will remain
as in the base edition and be noted in the provenance record.

## Validation

The completed increment must satisfy all of these checks:

1. `source.md` has exactly one title, one author line, and three chapter
   headings in order.
2. It begins with the Maul paragraph and ends with the tower crashing into
   shining shards.
3. The narrative contains no HTML tags, web navigation, images, PGA licence
   text, table of contents, horizontal separators, or promotional footer.
4. The complete narrative extracted from `source.md` matches the selected HTML
   after the documented mechanical normalisations.
5. The story readme records the source URL, edition details, retrieval date,
   checksum, conversion decisions, rights evidence, and any unresolved textual
   differences.
6. Markdown lint-style checks find no trailing whitespace, malformed headings,
   or replacement characters.
7. The repository is committed, pushed, and clean, with local `main` matching
   `origin/main`.

# Gamebook systems: background research and design guardrails

> **Status:** Background research; this is not a system specification<br>
> **Research date:** 20 July 2026<br>
> **Project scope:** A streamlined, print-capable gamebook system derived from
> Barry W. Brook's full RPG ruleset, initially tested by adapting Robert E.
> Howard's *The Tower of the Elephant*<br>
> **Purpose:** Establish the design lineage, identify useful techniques and
> recurrent failures, locate close precedents, and preserve room for an
> independently designed system

## Executive findings

Gamebooks do not form a single mechanical tradition. They occupy a spectrum
from books in which choices alone determine the path, through compact
stat-and-dice systems, to solo adventures that require an entire tabletop RPG.
The most useful precedents for this project sit at several different points on
that spectrum.

1. **The numbered passages are only the delivery mechanism.** The underlying
   design is a directed graph coupled to a small state machine. Choices create
   edges; health, skills, items, codewords and prior decisions determine which
   edges exist and what happens after they are followed.

2. **RPG-lite works best when every retained rule performs narrative work.**
   *Fighting Fantasy* demonstrates how three attributes and one standard combat
   loop can support an entire book. It also shows the cost of allowing a
   randomly generated combat score to dominate survival. *Lone Wolf* adds a
   stronger sense of character identity through selected Disciplines and
   campaign continuity. *Heart of Ice* goes further: its skills usually open
   qualitatively different routes rather than adding small numerical bonuses.

3. **A gamebook need not be a continually expanding tree.** Pure branching
   rapidly multiplies unwritten or rarely seen content. Foldback structures,
   local branches, bottlenecks and stateful reconvergence let later scenes
   remember earlier decisions without requiring a separate novel for every
   path. Choice of Games calls one version the “vignette” structure: branch
   within a scene, reconverge, and carry forward the consequences that matter
   as variables.

4. **Randomness is optional, and its job must be stated.** Dice can create
   suspense, uncertainty and replay variation. They can also overrule informed
   choices, make one starting character objectively worse, and force readers
   to repeat already-read material. Diceless skill gates, resource spends,
   deterministic costs and degrees of consequence are established
   alternatives.

5. **Combat is a design choice, not a compulsory gamebook ritual.** Repeating
   the same opposed roll until one endurance score reaches zero is compact but
   often asks the reader to make no decision. *Way of the Tiger* and some
   narrative-combat systems show that the important unit can instead be a
   tactical choice—approach, risk, sacrifice or escape—with the prose resolving
   the distinctive consequences of that choice.

6. **Full-RPG compatibility has a documented cost.** *Tunnels & Trolls*
   solitaire adventures prove that a persistent tabletop character can be used
   in a paragraph book. They also illustrate the burden of external rules,
   character generation, equipment accounting and encounter balance. Advanced
   Fighting Fantasy is valuable here as an inverse example: it expands a
   gamebook chassis into a group RPG, whereas this project intends to identify
   the small part of an existing RPG that a solo narrative actually needs.

7. **Open-world state is powerful but expensive.** *Fabled Lands* demonstrates
   revisitable locations, world-changing codewords and cross-book continuity.
   This is valuable research for an expandable system, but a bounded short-story
   adaptation does not need to begin as a sandbox. Local and global state should
   nevertheless be distinguished from the outset.

8. **Public-domain adaptation is already an active gamebook field.** ACE
   Gamebooks adapts classics including *Alice's Adventures in Wonderland*,
   *Beowulf* and *Dracula* with traditional RPG-like gamebook machinery.
   Choose Cthulhu explicitly converts Lovecraft's stories into branching books,
   generally without dice or character abilities. “A classic story made into a
   gamebook” is therefore a project category, not by itself an innovation.

9. **Novelty must come from a coherent, independently derived design.** Renaming
   *Fighting Fantasy*'s attributes, reproducing *Lone Wolf*'s combat table, or
   substituting another list of skills into *Heart of Ice* would be both weak
   design and an unnecessary intellectual-property risk. A stronger process is
   to trace each retained mechanic from the full RPG to a specific narrative
   function, record the transformation, compare it with the closest precedent,
   and validate it in play.

10. **The most promising territory is source-responsive rather than merely
    minimalist.** A reusable framework can define how to select and transform
    mechanics, while an individual story supplies the pressures that matter:
    stealth, resolve, accumulated danger, knowledge, relationships or physical
    cost. That is a research hypothesis for the design phase, not a decision
    already made.

## Scope, terminology and evidence standard

This review concentrates on prose gamebooks in which a solo reader makes
branching decisions and may maintain character or world state. It includes a
few tabletop and digital systems where they expose an especially useful design
principle. It is not a complete history of interactive fiction, parser games,
visual novels, solo journalling games or board games.

The following terms are used consistently:

- **Passage** means one numbered or otherwise addressable unit of prose.
- **Topology** means the arrangement of passages and links: tree, foldback,
  hub, bottleneck, loop and so on.
- **State** means information retained between passages: a score, skill, item,
  codeword, tickbox, relationship or prior choice.
- **Resolution** means the procedure used when the outcome of an attempted
  action is uncertain. A branch chosen by the reader is not automatically a
  “check”; it may simply be a decision with known trade-offs.
- **Gamebook** is the generic medium. “Choose Your Own Adventure” is the name
  of a specific, currently branded series and should not be used as the generic
  product description.
- **RPG-lite** means that a book retains selected roleplaying functions—such as
  capability, risk, attrition or progression—without importing a complete
  tabletop ruleset.

Source priority is: official or authorised rules; a designer's own account;
publisher material and book samples; specialist bibliographic databases; then
secondary summaries. Interpretations and recommendations in this document are
our analysis rather than claims made by the cited creators. Sources were
checked on the research date above. Commercial pages and living editions may
change.

## A short lineage of relevant approaches

The chronology matters because many apparently modern solutions were explored
early in the form's history.

- **1976 — *Buffalo Castle*.** Rick Loomis's solitaire for *Tunnels & Trolls*
  was among the earliest published paragraph adventures driven by a tabletop
  RPG character. It established the “external rules plus solo scenario” model.
  The [Gamebooks.org series record](https://gamebooks.org/Series/111/Show)
  documents the extensive line of *Tunnels & Trolls* solitaire adventures.
- **1976–79 — *Sugarcane Island* and Choose Your Own Adventure.** Edward
  Packard's manuscript was published in R. A. Montgomery's *Adventures of You*
  line before Bantam launched Choose Your Own Adventure in 1979. Its essential
  engine was second-person prose, explicit choices and multiple endings, with
  no general-purpose RPG character sheet. The publisher's
  [official history](https://www.cyoa.com/our-history/) records the lineage and
  the later series' range of successful, intermediate and fatal endings.
- **1982 — *Fighting Fantasy*.** *The Warlock of Firetop Mountain* combined the
  branching book with a compact, self-contained dice-and-stat system. The basic
  chassis became an influential British model for the RPG gamebook.
- **1983–85 — *Sorcery!*.** Steve Jackson extended the *Fighting Fantasy*
  foundation across a linked four-book campaign, with a substantial
  player-facing spell system and carried equipment.
- **1984 onward — *Lone Wolf*.** Joe Dever centred a persistent named
  protagonist, player-selected Disciplines and advancement across a long
  sequence. Project Aon's authorised editions make the original rules freely
  inspectable.
- **Mid-to-late 1980s — specialised systems.** *Way of the Tiger* made martial
  technique and tactical choice central. *Blood Sword* supported one reader or
  a party of up to four differentiated heroes. These systems show that a
  gamebook's rules can express its protagonist rather than simulate a generic
  adventurer.
- **1989 — Advanced Fighting Fantasy.** Marc Gascoigne and Pete Tamlyn expanded
  the gamebook rules into a referee-led tabletop RPG. The current
  [official overview](https://www.fightingfantasy.com/advanced-fighting-fantasy-1)
  identifies the original books and the 2011 second edition.
- **1990s — diceless and open-world designs.** The Virtual Reality series made
  selected skills, rather than dice, the principal means of differentiation.
  *Fabled Lands* used hubs, revisits, codewords, careers and cross-volume travel
  to create a persistent sandbox.
- **2000s onward — state-rich digital choice fiction.** ChoiceScript, ink and
  Twine made variables, conditional text and delayed consequences cheap to
  implement, while retaining the same graph-and-state fundamentals.
- **Contemporary revival — builds, parties and classic adaptations.**
  *DestinyQuest* emphasises equipment builds and quest maps; *Legendary
  Kingdoms* combines party play with an open world; ACE Gamebooks and Choose
  Cthulhu demonstrate continuing demand for interactive reworkings of classic
  literature.

## System studies

### 1. Choice without a general RPG layer: Choose Your Own Adventure

The classic Choose Your Own Adventure model stores almost everything in the
reader's current location. A choice sends the reader to another passage; the
path taken is usually the only state required. The official history notes that
early titles often approached forty endings, while later books sometimes had
as few as eight as individual paths became longer. It also records occasional
loops and a mixture of desirable, fatal and intermediate resolutions.
[Christian Swinehart's structural visualisations](https://samizdat.co/cyoa/)
make the variety visible as directed graphs rather than conventional tables of
contents.

**What it accomplishes**

- Immediate accessibility: book, reader and decisions are sufficient.
- Choices carry the full weight of play, without arithmetic interrupting prose.
- Numerous short paths support curiosity and replay.
- Outcomes can be tonal or narrative rather than measures of combat fitness.

**What it leaves unresolved**

- A path cannot easily remember earlier nuance unless it remains structurally
  separate or the prose asks the reader to remember it.
- Unsignposted choices can become arbitrary page selection. Choice of Games'
  [guidance on interesting choices](https://www.choiceofgames.com/2010/03/5-rules-for-writing-interesting-choices-in-multiple-choice-games/)
  argues that players need a basis for deciding and that one option should not
  be obviously superior.
- A large number of endings is not equivalent to sustained agency; many may be
  short failure twigs.

**Lesson for this project:** mechanics should earn their presence. A passage
choice can already represent judgement, intent and risk. A die roll or skill
check is useful only where uncertainty or character capability adds something
that the choice cannot.

**Guardrail:** use *gamebook*, *branching narrative* or *interactive novel* as
generic terms. Choose Your Own Adventure® is an active brand, as its
[official site](https://www.cyoa.com/our-history/) makes clear.

### 2. A complete RPG feeding a solo book: *Tunnels & Trolls* solitaires

The *Tunnels & Trolls* model predates the self-contained RPG gamebook. A player
creates a character under the tabletop rules, equips that character, then takes
it through a numbered solo adventure such as *Buffalo Castle*. Attribute-based
Saving Rolls and the RPG's combat, spell and equipment rules determine which
directions the text supplies. Many solos therefore assume a rulebook; some
later editions or introductory publications supplied abbreviated rules. The
[series bibliography](https://gamebooks.org/Series/111/Show) lists a long line
of these adventures, and a
[published sample solo](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/117944-sample.pdf)
shows Saving Rolls embedded directly in passage instructions.

**What it accomplishes**

- The same character can move between referee-led and solo play.
- Character creation, equipment and advancement have value beyond one book.
- A solo can test or develop a tabletop character without inventing a parallel
  ruleset.

**Costs**

- The reader may need another book before the story can begin.
- Full character generation and equipment accounting front-load effort.
- A general RPG contains rules that an individual story may barely use.
- Characters imported at different power levels make encounter and reward
  balance difficult.
- Repeated full combat procedures can dominate a short prose adventure.

**Lesson for this project:** derive, do not transplant. The full RPG gives us
the meaning and probability model from which to work, but the gamebook should
carry only the elements needed by its decisions and consequences. Compatibility
with a full RPG should be treated as a deliberate product requirement if it is
ever wanted, not as a free benefit.

### 3. The compact random-stat chassis: *Fighting Fantasy*

Most classic *Fighting Fantasy* books use three randomly generated attributes:
SKILL, STAMINA and LUCK. In the common rules, initial values are 1d6+6,
2d6+12 and 1d6+6 respectively. A test normally succeeds when 2d6 is less than
or equal to the relevant score. Testing Luck also reduces current LUCK by one,
so later tests become harder. In combat, each side rolls 2d6 and adds SKILL;
the higher attack strength usually inflicts two STAMINA damage. The
[Gamebooks.org system summary](https://www.gamebooks.org/Series/11/Show)
documents the complete basic loop, while the
[FightingFantasy.net authoring guide](https://fightingfantasy.net/articles/creating-a-fighting-fantasy-adventure-step-by-step-part-3)
confirms the test procedures and depleting Luck rule.

That design is economical. STAMINA is both combat endurance and a general
attrition budget. SKILL resolves fighting and many physical tests. LUCK is at
once a score, a diminishing resource and—in combat—an optional gamble over the
severity of damage. Iain Johnston's
[formal analysis of the combat system](https://arxiv.org/abs/2002.10172)
models optional Luck use as a resource-allocation problem rather than mere
flavour.

Its economy also exposes a structural weakness. Enumerating the standard 2d6
opposed roll gives the following per-round results before Luck or special
rules:

| Hero SKILL minus enemy SKILL | Hero wounds enemy | No wound | Enemy wounds hero |
| ---: | ---: | ---: | ---: |
| -3 | 15.90% | 8.02% | 76.08% |
| -2 | 23.92% | 9.65% | 66.44% |
| -1 | 33.56% | 10.80% | 55.63% |
| 0 | 44.37% | 11.27% | 44.37% |
| +1 | 55.63% | 10.80% | 33.56% |
| +2 | 66.44% | 9.65% | 23.92% |
| +3 | 76.08% | 8.02% | 15.90% |

These are exact enumerations of the 1,296 possible paired 2d6 outcomes. Because
initial SKILL spans 7–12, two legal starting heroes can experience the same
enemy as fundamentally different encounters. The first Luck test likewise
ranges from a 58.33% chance at LUCK 7 to certainty at LUCK 12; after four prior
tests those figures have fallen to 8.33% and 72.22%. Random generation is thus
part of the book's difficulty setting, whether or not it is described that way.

**What it accomplishes**

- A complete character and core loop fit on one adventure sheet.
- Rules are reusable across very different stories and genres.
- Combat and hazards can be inserted without adding bespoke logic passages.
- Depleting Luck gives the player at least one meaningful risk budget.

**Recurrent problems**

- A high or low initial SKILL can overwhelm later judgement.
- Combat often becomes repeated arithmetic with no decision between rounds.
- “Test your Luck” can substitute chance for a choice the prose ought to make
  interesting.
- Inventory objects frequently become hidden keys on a narrow “true path”.
- Sudden failure after a long route encourages cheating or rote replay rather
  than fresh decision-making.

**Lesson for this project:** compactness is worth preserving; the exact triad
and combat formula are not. A diminishing discretionary resource is more
interesting than a static “luck” attribute because it asks *when* the player is
willing to spend or gamble. Starting-character variation should express style,
not secretly select easy or hard mode.

**Guardrail:** do not reproduce the SKILL/STAMINA/LUCK package, its generation
formulae, its opposed attack-strength loop, its potion conventions, or its rule
wording. Even where individual procedures are not protected as such, that
recognisable bundle would make the result derivative in design terms.

### 4. Skills, campaign identity and a results table: *Lone Wolf*

The early *Lone Wolf* rules generate COMBAT SKILL as 10 plus a random digit and
ENDURANCE as 20 plus a random digit. More distinctive is the starting choice of
five out of ten Kai Disciplines. Camouflage, Tracking, Healing, Weaponskill,
Sixth Sense and other Disciplines both characterise Lone Wolf and create
conditional routes or benefits. The authorised
[Project Aon rules](https://www.projectaon.org/en/ReadersHandbook/Kai) and
[Kai Discipline list](https://www.projectaon.org/en/ReadersHandbook/KaiDisciplines)
record the generation and selection procedures.

Combat subtracts enemy COMBAT SKILL from the hero's adjusted score to obtain a
Combat Ratio. One random digit and that ratio are cross-referenced on a Combat
Results Table, which gives simultaneous, often asymmetric ENDURANCE losses.
Combat repeats until one side is defeated; evasion exists only when a passage
permits it. The exact procedure appears in Project Aon's
[combat rules](https://www.projectaon.org/en/ReadersHandbook/KaiCombat).

The series-level game is at least as important as the encounter loop. A
surviving hero carries scores, selected items and Disciplines into later books
and gains another Discipline after each completed adventure. This turns a
sequence of books into one long development arc.

**What it accomplishes**

- Discipline selection gives a named protagonist different viable emphases.
- Conditional Discipline choices make capabilities visible in the narrative.
- One table lookup resolves both sides' damage from one random input.
- Carry-over creates attachment and makes completion materially change the
  next book.

**Costs and risks**

- Some Disciplines may be much more useful in a particular volume than others;
  readers choose before knowing the book's needs.
- A low randomly generated COMBAT SKILL persists across the campaign unless
  compensated.
- Later books must accommodate many combinations of acquired skills and items.
- The combat table is efficient once learned but requires a separate lookup and
  is a particularly recognisable piece of expression.

**Lesson for this project:** selected capabilities and campaign continuity are
separate modules. The former may be useful in the first adaptation; the latter
should wait until a multi-story product is an actual requirement. Capability
choices should change approaches and information, not merely provide a hidden
optimal loadout.

**Guardrail:** do not reproduce the two-stat package, ten-Discipline structure,
random-number table, Combat Ratio/Results Table or Action Chart. The broad idea
of selecting capabilities is commonplace; its implementation should arise
independently from our RPG and source story.

### 5. Player knowledge as a capability: *Sorcery!*

Steve Jackson's four-volume *Sorcery!* sequence uses a *Fighting Fantasy*
foundation but allows the reader to play a warrior or a wizard. The wizard can
draw on a large spell list represented by three-letter mnemonics; many spells
require material components, and the text can offer codes that are inappropriate
or not genuine spells. The player must learn the repertoire well enough to
choose under narrative pressure. The series, its linked volumes and its
distinct spell system are described by the
[official Fighting Fantasy site](https://www.fightingfantasy.com/steve-jackson-s-sorcery)
and the [Gamebooks.org spellbook record](https://www.gamebooks.org/Item/104/Editions).

**What it accomplishes**

- The rules make the reader's memory and judgement part of wizardly expertise.
- Spell components convert inventory into planned capability rather than only
  keys.
- A warrior route provides a lower-overhead alternative.
- A linked campaign lets knowledge and possessions accumulate.

**Costs and risks**

- Memorisation and reference checking can interrupt reading.
- False or unsuitable spell options can feel like authorial traps rather than
  character decisions.
- Dozens of spells create a large content and balance burden.
- The coded spell vocabulary and component associations are distinctive.

**Lesson for this project:** knowledge can be a resource, and choosing *how* to
act can be richer than checking whether a generic score succeeds. The reader
should have enough evidence to reason, and failure should reveal or change
something rather than merely punish imperfect recall.

### 6. The inverse transformation: Advanced Fighting Fantasy

Advanced Fighting Fantasy is a referee-led group RPG descended from the
gamebooks, not another branching-book format. Its significance here is
methodological. The original 1989 line expanded the compact chassis with
Special Skills, Talents, magic, equipment, creatures, a setting and a Director;
the second edition continues that full-RPG direction. The
[official overview](https://www.fightingfantasy.com/advanced-fighting-fantasy-1)
sets out the publication history, and a
[current publisher sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/453554-sample.pdf)
shows heroes described by SKILL, STAMINA, LUCK, MAGIC, Special Skills, Talents
and equipment.

AFF answers the question “what must be added when a human referee and an
open-ended group replace the bounded book?” Our project asks the reverse:
“what can be removed when authored passages replace the referee?” In a
gamebook, the prose already controls opposition, timing, environment and
available actions. It need not carry general procedures for every possibility
a tabletop group might invent.

**Lesson for this project:** conduct the reduction by function. For each RPG
subsystem, ask what reader decision or story consequence it would support in
the adaptation. If the book can express that function directly and more
clearly, the subsystem can be omitted or transformed.

### 7. Diceless capability-gating: Virtual Reality and *Heart of Ice*

The Virtual Reality series removed dice and commonly let the player choose four
skills from twelve. Skills open routes, permit methods and mitigate costs. Dave
Morris's surviving
[1993 author guidelines](https://fabledlands.blogspot.com/2018/03/so-you-want-to-write-gamebook.html)
are unusually valuable primary design evidence. They require the book to be
completable with any four-skill combination, recommend roughly equal and
repeated use of skills, and propose at least three substantial early strands
that gradually converge towards the climax. Morris also argues that the story
must remain enjoyable and internally logical rather than becoming an arbitrary
sequence of tests.

In *Heart of Ice*, four chosen skills, Life Points, possessions and codewords
provide almost all persistent state. A
[published sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/478171-sample.pdf)
shows the compact rules and adventure sheet.

**What it accomplishes**

- Character differentiation is chosen, not rolled.
- A skill often grants a qualitatively different action rather than a small
  modifier.
- No dice or lookup table is required during reading.
- Different builds naturally support different routes and replay.

**Design burden**

- Every legal build must remain viable; otherwise character creation contains
  concealed failure states.
- Skills need comparable value, frequency and narrative range.
- Explicitly displaying unavailable skill options can reveal paths the current
  reader cannot take.
- Binary capability gates can become automatic answers if the surrounding
  decision has no trade-off.

**Lesson for this project:** this is probably the closest mechanical comparator
if our cut-down RPG emphasises expertise over repeated random checks. It also
sets a demanding fairness standard: no “wrong build”, no single indispensable
capability, and no skill that simply replaces three others.

**Guardrail:** do not substitute our own labels into the choose-four-of-twelve
architecture. We should derive the number, granularity and use of capabilities
from the full RPG and *Tower*'s actual decision space.

### 8. Protagonist-specific tactics: *Way of the Tiger*

*Way of the Tiger* gives its ninja protagonist multiple combat techniques with
different hit and damage profiles, plus Defence, Endurance, blocking, limited
Inner Force, Fate and selected ninja skills. Its
[series record](https://www.gamebooks.org/Series/469/Show) and a
[rules sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/527552-sample.pdf)
show a system deliberately built around the fiction of a trained martial
artist.

The important distinction from routine gamebook combat is that a round can ask
which technique or risk posture to use. The rules thereby express character
knowledge and make conflict interactive after the decision to fight has been
made.

**Lesson for this project:** story-specific mechanics can be reusable at the
framework level without being generic at the surface level. A framework might
define “approaches with different risks and costs”, while a particular story
defines what those approaches mean. The cost is rules weight: several technique
tables are justified only if combat is a central pleasure of the source.

### 9. Solo or party play: *Blood Sword*

*Blood Sword* supports a single reader controlling one hero or a group of up to
four differentiated archetypes. Battle order, specialised powers and passages
addressed to particular characters let party composition change available
information and tactics. Dave Morris describes solo-or-team play as the
series' distinguishing proposition in his
[retrospective](https://fabledlands.blogspot.com/2014/08/blood-sword-redux-demons-claw.html);
the [series bibliography](https://gamebooks.org/Series/56/Show) and
[rules sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/478195-sample.pdf)
document its party structure.

**Lesson for this project:** party roles, private information and co-operative
play are established gamebook possibilities, but they multiply passage logic
and bookkeeping. They are outside the first story's stated need unless the
adaptation later gives a compelling reason to control more than one character.

### 10. Persistent open worlds: *Fabled Lands*

*Fabled Lands* replaces a single quest corridor with revisitable locations,
regional hubs, careers, trade, quests, possessions, rank and travel between
volumes. Its crucial innovation for this review is state architecture. A
codeword can record a world change whose consequences appear in several
locations; a local tickbox can record a change relevant only where it happened.
Dave Morris explains that distinction, and the authoring trade-off between
separate logic-gate passages and longer conditional passages, in
[“Two styles of gamebook design”](https://fabledlands.blogspot.com/2022/02/two-styles-of-gamebook-design.html).
A [sample of the first volume](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/528417-sample.pdf)
shows the larger character sheet and navigable structure.

**What it accomplishes**

- The reader can choose goals and order rather than only routes.
- Revisits reveal persistent consequences.
- Books can connect into one larger playable geography.
- Local and global flags prevent every event from requiring a permanent new
  branch.

**Costs and risks**

- Bookkeeping and condition checking can become the dominant activity.
- Hubs permit grinding, economic exploits and accidental repetition.
- A large state space is difficult to test exhaustively.
- Freedom of movement can weaken pace and thematic escalation.
- Physical books must expose some conditional logic to the reader or consume
  extra numbered passages hiding it.

**Lesson for this project:** adopt the distinction between local and global
state, not the open-world scope. A short-story adaptation can use a few local
changes and perhaps one or two global consequences while retaining a strong
dramatic arc. Cross-story persistence should wait for evidence that the planned
corpus benefits from it.

### 11. Build-and-loot progression: *DestinyQuest*

*DestinyQuest* brings the structure of a digital action RPG into a large
gamebook: map-selected quests, equipment slots, many item combinations, special
abilities and extensive hero customisation. The
[official site](https://www.destiny-quest.com/) and
[downloadable play aids](https://www.destiny-quest.com/downloads/) make that
emphasis explicit. Author Michael J. Ward's
[retrospective starting guide](https://www.destiny-quest.com/news/destinyquest-so-where-do-i-start/)
also acknowledges that balance and accessibility improved after the first
book.

**Lesson for this project:** physical books can support substantial character
builds, but the content then rewards optimisation, loot comparison and repeat
combat. That is a valid play style, not a neutral enhancement. It would pull a
Howard adaptation towards an equipment game unless the source and the full RPG
make that focus intentional.

[*Legendary Kingdoms*](https://gamebooks.org/Series/2125/Show)
is a related modern combination: an open world controlled by a party, with
trade, ships, armies and world state. It is useful as a later scalability
comparator, but it is further from the initial one-protagonist, one-story
problem.

### 12. The closest product-category precedents: ACE Gamebooks and Choose Cthulhu

ACE Gamebooks explicitly markets interactive reworkings of classic literature.
The line includes *Alice's Nightmare in Wonderland*, *Beowulf Beastslayer* and
*Dracula: Curse of the Vampire*, among others. The
[official overview](https://www.acegamebooks.com/about-ace-gamebooks) presents
the classic-adaptation proposition, while the
[Gamebooks.org series record](https://gamebooks.org/Series/1734/Show) documents
dice or custom-card randomisation, multiple playable characters in some books,
and character play aids. *Dracula* has 1,000 passages and multiple canonical
protagonists with character-specific attributes, according to its
[bibliographic record and errata](https://gamebooks.org/Item/12609/Show).

Choose Cthulhu occupies a different point in the same category. Its
[project description](https://choosecthulhu.es/en/what-is-choose-cthulhu/?v=da4b060a2e90)
says that it adapts Lovecraft's stories themselves rather than merely using the
setting. Its standard books use 100 playable passages, generally omit dice and
special abilities, preserve the canonical ending alongside new alternatives,
and lighten prose to make repeated reading less tedious.

Together these precedents establish that all of the following are already in
use:

- a public-domain or classic literary source;
- second-person conversion;
- a canonical route plus invented alternatives;
- traditional attribute-and-combat gamebook rules;
- diceless first-generation branching;
- multiple playable characters from the source;
- bespoke attributes for an individual adaptation;
- visual and marketing cues that invoke 1980s gamebooks.

The implication is constructive: our differentiation must reside in the
adaptation method, mechanics and resulting play—not in the source-selection
premise alone. The clearest independent basis is the stated one: a deliberate
reduction of Barry's RPG, tested against the narrative structure and themes of
each source work.

**Guardrail:** do not emulate ACE's attribute package, custom-card solution,
bookmark/character-sheet presentation, multi-character structure or “classics
as never before” branding as a bundle. Do not adopt Choose Cthulhu's
100-passage/mostly pure-branching template by default. Any similar feature needs
an independently recorded reason.

### 13. Digital narrative systems as authoring research

Digital tools are relevant even if the eventual product is a printed book.
They make the graph-and-state model explicit.

ChoiceScript usually controls exponential branching by creating local branches
inside chapters or vignettes, reconverging, and retaining consequences in
variables. Its
[vignette design note](https://www.choiceofgames.com/2010/01/vignette-structure-as-a-means-of-controlling-branching/)
points out that ten fully independent binary choices would require 1,024 end
pages. Stats can instead carry the decisions that matter into shared later
scenes. The system's
[choice-design guidance](https://www.choiceofgames.com/2010/03/5-rules-for-writing-interesting-choices-in-multiple-choice-games/)
emphasises consequences, informed decisions and the absence of an obviously
dominant option.

[ink](https://www.inklestudios.com/ink/) represents narrative as knots,
stitches, choices, diverts, gathers, variables and conditions; its
[writing manual](https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md)
is a practical account of stateful reconvergence. [Twine](https://twinery.org/)
offers a visual passage graph and story formats with variables and conditional
logic. These tools do not decide good topology, but they expose unreachable
passages, state dependencies and combinatorial growth more clearly than an
unstructured manuscript.

**Lesson for this project:** keep the design representation independent of
presentation. A passage, link, condition and state change can be modelled in a
tech-neutral source even if the first output is Markdown or print. No authoring
technology needs to be selected yet.

### 14. Additional approaches screened

Several neighbouring traditions do not need full dossiers for the first design
increment, but they close important gaps in the survey.

- **Cretan Chronicles** adapts Greek myth through a fixed heroic role and
  story-responsive state: Might, Protection, wound levels, divine favour, and
  paired Honour and Shame. Its unusual “taking a hint” rule lets a reader try
  an unlisted action by applying a numerical transformation to the current
  passage. The intention—to reward initiative beyond menu choices—is valuable;
  the implementation can make the character perform an action the reader did
  not intend. The [series record](https://gamebooks.org/Series/96/Show) makes
  this a useful comparator for moral resources, myth adaptation and the danger
  of concealed verbs.
- **Advanced Dungeons & Dragons Adventure Gamebooks** use a pre-created
  character whose attributes can be customised, add those attributes to dice
  rolls, and sometimes provide limited experience points that can influence
  checks. They preserve class, spell and setting identity while resolving
  combat more like another check than a full monster-by-monster battle. The
  [series record](https://gamebooks.org/Series/21/Show) shows another way to
  reduce a large RPG without requiring its rulebook.
- **Middle-earth Quest** takes the opposite, layered approach: basic rules,
  advanced time and travel, optional character creation and compatibility with
  the full Middle-earth Role Playing system. Some volumes use hex maps for
  freer movement. Its [bibliographic history](https://www.gamebooks.org/Series/270/Show)
  also records a format-specific licensing dispute and recall—a reminder that
  permission for a game or setting does not automatically cover every kind of
  publication.
- **Sherlock Holmes Solo Mysteries** shifts the centre of play from fighting to
  investigation. A created or pre-generated investigator uses six abilities,
  while codes retain clues, deductions and prior decisions for the eventual
  accusation. Some checks have partial results. The
  [series record](https://gamebooks.org/Series/389/Show) is particularly useful
  for future public-domain mysteries: information state can be the game, though
  rolling to see whether an already-signposted clue is visible can feel
  artificial.
- **Forbidden Gateway** uses physical and mental attributes, but its more
  interesting reported feature is encounter-specific conflict: different
  strategies lead through different passages and tests instead of every enemy
  entering one repeated combat loop. The
  [specialist record](https://gamebooks.org/Series/173) supports the principle
  that major conflicts can be authored as narrative problems.
- **Falcon** combines a persistent time-agent identity, psychic and physical
  modifiers, codewords/items and end-of-mission scoring. The
  [series record](https://gamebooks.org/Series/146/Show) shows that a book can
  evaluate how a mission was completed, not only whether the final passage was
  reached. The separate [Time Machine line](https://gamebooks.org/Series/78/Show)
  uses a single successful ending and historical exploration, but also shows
  how a supposedly non-fatal structure can trap an ill-equipped reader in a
  loop.
- **GrailQuest** uses a fixed protagonist, persistent Life and Experience,
  spells, comic narration, special “Dreamtime” passages and occasional physical
  activities. Its [series record](https://gamebooks.org/Series/188/Show)
  demonstrates that tone and recurring character voice can differentiate a
  gamebook even when the underlying rules are conventional.
- **Be an Interplanetary Spy** combines short branching prose with mazes,
  pattern recognition, visual puzzles and material page interaction. The
  [series record](https://gamebooks.org/Series/6/Show) is a useful reminder that
  “mechanics” can live in illustration and book handling rather than on an
  adventure sheet.
- **Paired-book systems** occupy a separate branch of the medium. TSR's
  [1 on 1 Adventure Gamebooks](https://gamebooks.org/Series/291/Show) give two
  players separate books and sometimes ask each to control opposition for the
  other; [*Ace of Aces*](https://gamebooks.org/Series/18/Show) and
  [*Lost Worlds*](https://gamebooks.org/Series/49/Show) cross-reference
  simultaneous choices between books to resolve duels. These are outside the
  initial solo prose brief, but prevent us from treating multiplayer or
  cross-book lookup as new territory later.

These examples reinforce the same conclusion: innovation can come from moral
state, investigation, scoring, unprompted action, visual puzzles, layered rules
or multiplayer information. Adding all of them would produce incoherence. The
source and intended reader experience must select the mechanism.

## Comparative map

The table compresses the main precedents by what the reader actually does. It
is deliberately functional: surface vocabulary is less important than the
relationship between decisions, uncertainty and retained state.

| Family or example | Character and retained state | Resolution | Dominant topology | Principal strength | Principal warning |
| --- | --- | --- | --- | --- | --- |
| Choose Your Own Adventure | Current passage; occasionally remembered path | Reader choice | Diverging paths and endings | Frictionless access | Arbitrary choices and shallow failure twigs |
| *Tunnels & Trolls* solos | Full tabletop character, equipment, spells and advancement | RPG Saving Rolls and combat | Scenario paths around RPG encounters | One character crosses solo and group play | External rules and imported baggage |
| *Fighting Fantasy* | Three scores, inventory, provisions and story keys | 2d6 tests and repeated opposed combat | Foldback quest, often with a narrow winning route | Very compact universal chassis | Random SKILL dominance; non-decisional combat |
| *Lone Wolf* | Two scores, selected Disciplines, inventory and cross-book progress | Random digit plus combat table; conditional skills | Directed quest in a long campaign chain | Persistent protagonist and capability identity | Loadout imbalance and table dependence |
| *Sorcery!* | FF-like scores plus spells, components and campaign inventory | Dice plus player knowledge | Linked campaign with role-specific routes | Rules make magical knowledge playable | Lookup, memory tax and trap options |
| Virtual Reality / *Heart of Ice* | Four selected skills, Life, possessions and codewords | Mostly deterministic skill and item gates | Multiple substantial strands that converge | Build identity without dice | Any legal build must remain viable |
| *Way of the Tiger* | Fixed specialist with combat techniques, skills and limited resources | Technique-specific rolls and tactical choices | Quest with bespoke conflicts | Mechanics express the protagonist | Rules density if specialised combat is not central |
| *Blood Sword* | One to four role-specialised heroes | Tactical combat and character-specific options | Party quest | Solo/co-operative role differentiation | Combinatorial party and battle logic |
| *Fabled Lands* | Abilities, career, rank, possessions, money, codewords and local flags | Checks, combat and state gates | Hubs, loops and cross-book travel | Persistent open world | Bookkeeping, exploits and weak pacing |
| *DestinyQuest* | Equipment build, abilities, career and quest progress | Combat strongly modified by build | Map-selected quest clusters | Deep optimisation and reward loop | Loot/combat can displace story |
| ACE Gamebooks | Title-specific stats, items, dice/cards and sometimes multiple protagonists | Traditional RPG-gamebook procedures | Large branching adaptations | Direct precedent for mechanics-rich classics | Category and feature overlap with this project |
| Choose Cthulhu | Minimal state; occasional title-specific puzzle state | Choice, generally without dice or abilities | About 100 passages with canonical and alternate endings | Direct, accessible story adaptation | Adaptation premise alone is not distinctive |
| ChoiceScript / ink / Twine | Arbitrary variables and conditional content | Authored logic; optional randomness | Local branches with stateful reconvergence | Delayed consequence without endless divergence | Hidden state and stat optimisation can obscure agency |

## Branching topology: controlling the content explosion

If every choice creates two permanently separate paths, the number of leaf
passages doubles at each layer. Ten such choices imply 1,024 leaves before any
path has meaningful length. This is why most substantial gamebooks use several
topologies together.

### Pure divergence

Each choice produces a distinct future, often ending soon. This is effective
for short books, comic outcomes and highly divergent endings. It gives the
strongest visible causality and the poorest reuse of prose. Excessive use turns
failure into disposable content and rewards rapid page sampling rather than
sustained play.

### Branch-and-bottleneck, or foldback

Paths separate, deliver different events, then meet at a shared scene. This
keeps the manuscript finite and gives the narrative a controlled dramatic arc.
Its weak form makes choices cosmetic because every route arrives unchanged.
Its strong form changes the state carried into the shared passage: injuries,
knowledge, allies, suspicion, time or available tactics.

### Stateful reconvergence

Paths rejoin physically while later conditions preserve their important
effects. This is the print analogue of ChoiceScript's vignette model. It offers
a high return per passage, but only if state is selective. Recording every past
detail produces an unreadable character sheet; recording nothing makes agency
illusory.

### Capability-gated parallel routes

Selected skills or possessed items reveal different methods through the same
problem. *Heart of Ice* is the clearest example. This supports character
identity and replay without multiplying every later scene. It becomes trivial
when possession of the capability automatically reveals the best answer, and
unfair when one unadvertised capability is essential.

### Hub and spoke

A central location links to several excursions and can be revisited. Hubs give
the player control over order and can make accumulated changes visible. They
also enable repetitive loops, grinding and chronology errors. Local completion
flags and clear exit pressure are needed when the story is meant to escalate.

### Open-world network

Many locations interlink and remain available. World state, travel rules and
economic systems replace a single main quest as the organising structure.
This is the achievement of *Fabled Lands*, but it is a different authoring and
testing problem from adapting a tightly plotted short story.

### Campaign chain

Each book has a bounded graph, while selected character state crosses the
boundary into the next. *Lone Wolf* and *Sorcery!* use this to make completion
part of character growth. It creates backwards-compatibility obligations:
later volumes must support new readers, veterans with different histories, or
both.

### Quest map

A visual map or menu lets the reader select relatively self-contained missions.
*DestinyQuest* uses this to provide build progression and adjustable order
without a fully simulated world. It is efficient for a sequence of encounters,
but less natural for fiction whose causal sequence matters.

### Party-role graph

Passages depend on which characters are present, alive or acting. This can
generate excellent private knowledge and complementary expertise. It also
multiplies conditional prose and complicates a single-reader adventure sheet.

No one topology is the “gamebook structure”. The likely robust pattern for a
bounded literary adaptation is a dramatic spine with substantial local
branches, selective stateful reconvergence and more than one viable route
through key problems. That remains a hypothesis to test against the source,
not a settled template.

## State architecture: remember only what can matter

A gamebook can be described as the current passage plus a state vector. The
practical question is not how many variables are possible, but which memories
create a later decision or consequence.

| State class | Examples in prior systems | Narrative function | Main risk |
| --- | --- | --- | --- |
| Vital resource | STAMINA, ENDURANCE, Life Points | Accumulated bodily danger and survival | Generic hit-point tax |
| Depleting decision resource | Luck, Inner Force, limited spell use | Lets the player alter risk or intensity at chosen moments | Hoarding, optimal-spend puzzle or sudden exhaustion |
| Capability | Discipline, skill, spell, technique | Opens methods, information or exemptions | Hidden mandatory build; one capability subsumes others |
| Inventory | Weapon, component, key, evidence | Preparation, opportunity and concrete continuity | “Find the exact object or fail” scavenger route |
| Local event flag | Tickbox at one location | Records a change relevant on revisit | Too many marks for one-off details |
| Global world flag | Codeword | Propagates a consequential event to several locations | Long opaque lists and missed checks |
| Relationship or reputation | Trust, fear, allegiance | Carries social choices into later scenes | Reducing characters to visible meters |
| Knowledge | Clue, password, witnessed fact | Rewards exploration and attention | Reader knows it but sheet says character does not, or vice versa |
| Position and time | Location, turn count, pursuit clock | Creates routes, deadlines and opportunity cost | Logistics overwhelms prose |
| Campaign progress | Rank, acquired skill, surviving ally | Makes one book alter the next | Escalation and compatibility burden |

Three rules follow from this survey:

1. **Every recorded state needs a future consumer.** If no later choice,
   condition or consequence reads it, it is administrative noise.
2. **Use the narrowest scope.** A local mark is better than a global codeword
   when the fact matters in only one place. A transient passage choice is
   better than either when the consequence is immediate.
3. **Prefer semantic state to incidental state.** “The guards distrust you” is
   more reusable and testable than separate flags for every sentence that
   contributed to their distrust—unless those details need different later
   effects.

For print, visibility is also a design decision. Asking “if you have codeword
X” exposes the existence of a condition. Hiding the check behind an extra
passage protects discovery but consumes passage numbers and page turns. Morris's
[comparison of codewords, tickboxes and logic-gate passages](https://fabledlands.blogspot.com/2022/02/two-styles-of-gamebook-design.html)
shows that there is no cost-free representation.

## What RPG-lite mechanics are for

The review suggests six legitimate functions for retained RPG machinery. A
proposed rule should identify at least one of them.

### Express capability

The rule distinguishes what this protagonist can attempt or how they approach
it. Selected skills, Disciplines and techniques do this directly. A numerical
bonus does it weakly unless the difference changes the decision.

### Resolve genuine uncertainty

The player chooses an action whose outcome cannot be known. Randomness is most
defensible when uncertainty is intrinsic to the fiction and both success and
failure create playable consequences. It is least defensible when it follows a
pure guess or repeats until death.

### Accumulate consequence

Health, stress, exposure, suspicion or time can make earlier choices matter
later. The resource should describe the source's danger, not automatically be
called hit points. Recovery opportunities and failure thresholds determine
whether it creates tension or merely attrition.

### Create discretionary leverage

A limited resource can let the player improve an outcome, avoid a cost, reveal
an option or persist after failure. *Fighting Fantasy*'s optional use of Luck
illustrates the value of timing a scarce intervention, even though its exact
implementation need not be retained.

### Support preparation and discovery

Inventory, knowledge and allies make exploration pay off. The healthy version
creates several useful preparations or lets an item alter the cost of a later
problem. The unhealthy version hides one mandatory key on one mandatory path.

### Sustain identity across stories

Advancement and carry-over can make a series feel continuous. This function is
irrelevant until more than one playable story exists and their compatibility
contract is known.

The reduction test for every subsystem in the full RPG should therefore be:

1. What player decision does this subsystem create?
2. What fictionally meaningful uncertainty or consequence does it represent?
3. Can an authored branch express that function more cleanly?
4. What bookkeeping does it impose per use and over a whole playthrough?
5. Does it interact with at least one other rule, or is it an isolated ritual?
6. What happens on failure, and is that result worth reading?
7. What closest published mechanic would a reader compare it with?

If the answers are weak, omission is a design result rather than a loss of RPG
fidelity.

## Recurrent design failures and their controls

### Arbitrary choice

**Symptom:** two doors, roads or plans are offered without evidence of their
likely differences.<br>
**Effect:** the player selects randomly and disengages from responsibility for
the outcome.<br>
**Control:** provide clues, competing values, explicit uncertainty or a
character-informed basis for judgement. Surprise can remain in the result; the
decision still needs a reason.

### The single true path

**Symptom:** victory requires an exact sequence of obscure choices and items.<br>
**Effect:** replay becomes route memorisation, and apparent agency conceals a
password hunt.<br>
**Control:** provide multiple viable strategies, substitute resources, or
graded endings. Reserve precise sequence puzzles for stories that make
deduction itself the advertised challenge.

### Starting-stat tyranny

**Symptom:** a random initial score controls most later checks or combat.<br>
**Effect:** character generation selects difficulty before the player has made
an informed decision.<br>
**Control:** fixed baselines, point choice with genuine trade-offs, narrow
variation, bounded bonuses, or resolution in which capability changes cost and
options rather than basic viability.

### Combat without decisions

**Symptom:** roll, compare and subtract repeatedly until one side reaches zero.<br>
**Effect:** the dramatic centre of an adventure becomes clerical work.<br>
**Control:** resolve minor conflict once; make major conflict a sequence of
fiction-specific choices; allow changes of stance, objective, cost and escape;
or omit combat where the source does not need it.

### Failure as lost reading time

**Symptom:** one unlucky check near the end sends the reader back to passage
one.<br>
**Effect:** the primary penalty is rereading known prose, which encourages
bookmarking and ignored dice.<br>
**Control:** fail forward, impose a cost, change position or knowledge, offer
checkpoints, or reserve terminal failure for decisions whose stakes are clear.

### Capability as an automatic answer

**Symptom:** if a listed skill is present, selecting it is always superior.<br>
**Effect:** character creation made the decision earlier; the current choice is
ceremonial.<br>
**Control:** give capabilities more than one possible use, attach costs or
trade-offs, and let ordinary actions remain viable.

### The wrong build

**Symptom:** a legal starting selection cannot finish or is markedly inferior.<br>
**Effect:** the reader loses because of information unavailable during
character creation.<br>
**Control:** use Morris's Virtual Reality standard as the default test: every
legal build can complete, while doing so through materially different routes
or costs.

### Bookkeeping without payoff

**Symptom:** many values change frequently but rarely affect a decision.<br>
**Effect:** the game feels more complex without becoming deeper.<br>
**Control:** delete unused state, collapse correlated variables, and measure
marks/lookups per passage during playtests.

### Cosmetic reconvergence

**Symptom:** branches return to the same passage with the same state and no
later acknowledgement.<br>
**Effect:** the reader detects that the choice changed only a paragraph.<br>
**Control:** preserve at least one material difference—cost, knowledge,
relationship, position, future option or prose acknowledgement—when the choice
was framed as consequential.

### Rules-fiction mismatch

**Symptom:** the rules reward behaviour the protagonist or source would not
recognise, or translate every danger into generic fighting ability.<br>
**Effect:** the adaptation becomes a familiar dungeon game wearing the source's
names.<br>
**Control:** derive mechanics from recurring pressures in the actual text and
test whether each result can be narrated naturally.

### Full-RPG residue

**Symptom:** a subsystem survives because it exists in the parent RPG, despite
having few meaningful uses in the book.<br>
**Effect:** the reader learns and records rules that the authored story has
already made unnecessary.<br>
**Control:** apply the functional reduction test above and record deliberate
omissions as part of the design rationale.

## Adapting a fixed literary work

An original gamebook can invent its plot around its branches. An adaptation
starts with a completed causal and thematic structure. Its central challenge
is to add agency without either reducing choices to decoration or dissolving
the source into a generic adventure.

### Distinguish four kinds of source material

1. **Narrative invariants** are events, revelations, relationships or images
   whose removal would make the adaptation cease to represent this work. They
   need not occur identically on every path, but the design should state what
   is being preserved.
2. **Decision seams** are moments where the source protagonist assesses,
   chooses, withholds, risks, trusts, investigates or changes tactics. These are
   natural places to transfer agency to the reader.
3. **Elastic intervals** are journeys, searches, preparations, conversations
   and conflicts whose method can vary without breaking the work's identity.
   They provide room for substantial branches.
4. **Counterfactual boundaries** mark how far an alternate path may depart.
   Some may change route and cost while returning to a canonical event; others
   may support a non-canonical ending. The book should know which kind it is
   offering.

### Preserve more than plot points

Source fidelity has several dimensions:

- **Causal:** later events still arise from intelligible earlier causes.
- **Character:** available actions remain credible for the playable
  protagonist, or changes to that role are explicit.
- **Thematic:** the rules reinforce the work's concerns rather than rewarding a
  contrary game loop.
- **Tonal:** repetition, scoring and failure text do not turn horror, tragedy or
  wonder into unintended farce.
- **Linguistic:** public-domain source language may be retained selectively,
  but interactive passages need clarity and consistency of person and tense.
- **Historical:** offensive or obsolete material is handled by a recorded
  editorial policy rather than silently drifting between editions.

### A preliminary lens for *The Tower of the Elephant*

This is not a proposed passage map. It identifies why the story is a useful
test case.

The source has a strong, bounded physical objective and setting: Conan hears of
the jewel, enters the tower precinct, encounters Taurus, ascends, survives the
tower's guardians, meets Yag-kosha and participates in the revenge that destroys
Yara and the tower. It combines stealth, physical danger, alliance, curiosity,
supernatural revelation and a morally charged request. Those pressures are
more varied than “fight monsters until treasure is found”.

Likely invariants include the tower and Heart of the Elephant, the revelation
of Yag-kosha's captivity, and the relationship between that captivity, Yara and
the ending. Likely seams include how Conan gathers information, approaches and
enters the grounds, responds to Taurus, handles obstacles, explores the upper
chambers and responds to Yag-kosha. The key research question is how much
counterfactual freedom can be added before Conan no longer behaves like Howard's
Conan or the revelation loses its force.

A useful working concept is **canonical pressure**: the source exerts a
gravitational pull towards its defining events, while player choices alter the
route, knowledge, relationships, cost and possibly the ending. This term names
a design problem; it is not yet a mechanic. It could produce meaningful agency
with fewer invented plot branches than a wholly open retelling, but only
playtesting can show whether it feels consequential or railroaded.

Before rules are designed, the story should be annotated for invariants, seams,
elastic intervals, hazards, knowledge transitions and plausible consequences.
That source map will be more informative than beginning with a generic list of
attributes.

## Design-space map and novelty hypotheses

“Novel” has two meanings that should not be confused. Here it means a system
with a distinctive, coherent play experience and an independently documented
design. It does not assert patent novelty, legal protectability or absence of
all prior art.

### Axes on which gamebook systems differ

| Axis | One end | Other end |
| --- | --- | --- |
| Source of outcomes | Deterministic choice and gates | Frequent random resolution |
| Character definition | Fixed canonical protagonist | Broad player-created build |
| Mechanical surface | Universal system across stories | Story-responsive mechanics |
| Branch structure | Directed dramatic spine | Open revisitable world |
| Persistence | One-play state | Multi-book campaign state |
| Conflict | Abstract repeated combat | Bespoke narrative/tactical sequence |
| Failure | Terminal restart | Graded cost, displacement or altered ending |
| Source fidelity | Free reimagining | Strong canonical invariants |
| State visibility | Minimal or reader-visible | Hidden, computed or heavily conditional |
| Bookkeeping | None or a few marks | Detailed sheet, inventory and progression |

Well-known clusters already occupy much of this space:

- choice-only divergence with multiple endings — classic CYOA;
- universal random stats, combat and inventory — *Fighting Fantasy* and many
  descendants;
- selected skills plus campaign advancement — *Lone Wolf*;
- diceless selected-skill gates — Virtual Reality / *Heart of Ice*;
- full RPG character in a solo scenario — *Tunnels & Trolls*;
- persistent open-world simulation — *Fabled Lands*;
- equipment-build and combat optimisation — *DestinyQuest*;
- traditional RPG-gamebook adaptation of classics — ACE Gamebooks;
- light, mostly choice-only adaptation of original stories — Choose Cthulhu.

The research found less direct coverage of the following *combination*:

- a fixed literary protagonist rather than a generic avatar;
- mechanics selected through a documented reduction of a larger RPG;
- those mechanics customised to recurring pressures in each source while
  preserving a stable cross-book framework;
- informed choices carrying most agency;
- uncertainty used selectively, with failure changing cost, position,
  knowledge or relationships more often than ending play;
- very low, transparent bookkeeping;
- explicit canonical invariants combined with substantial freedom in route and
  consequence;
- a reproducible adaptation method that can be applied to unrelated
  public-domain stories.

That is a promising research direction, not proof that the combination is
unprecedented. A wider commercial and patent search, direct play of the closest
books, and comparison against the actual proposed rules will be required before
making any public novelty claim.

### Candidate innovation hypotheses

These are questions to test during design, not features to adopt wholesale.

1. **Function-first reduction:** can every gamebook rule be traced to one
   function in the parent RPG and one recurring pressure in the source story?
2. **Source-responsive vocabulary:** can a stable core procedure support
   story-specific resources without producing a different game in every book?
3. **Consequential failure:** can most failed resolutions create an altered
   situation instead of death or a simple numerical loss?
4. **Canonical pressure:** can a literary work's defining events remain
   recognisable while route, cost, knowledge and moral involvement genuinely
   belong to the player?
5. **Capability as changed affordance:** can expertise change which actions are
   available or safe, rather than add a small bonus to a universal roll?
6. **Bookkeeping budget:** can the complete playable state fit in a few plainly
   meaningful marks, with a measured maximum number of updates and lookups per
   passage?
7. **Adaptation grammar:** can invariants, seams, elastic intervals and
   counterfactual boundaries become a repeatable pre-design process for other
   public-domain works?

The strongest innovation is likely to be the interaction among these choices,
not an isolated die formula. A unique randomiser attached to a familiar
stat-combat loop would be superficial differentiation.

## Intellectual-property and originality guardrails

This section is a practical design boundary, not legal advice. Rights differ by
jurisdiction, publication territory, source work and edition. Obtain qualified
advice before commercial release if the final product raises material doubt.

### The legal baseline

The Australian Attorney-General's
[copyright overview](https://www.ag.gov.au/rights-and-protections/copyright/copyright-basics)
states that copyright protects original expression of ideas and information,
not the ideas or information themselves. Literary text, artwork, maps, diagrams,
software and published editions can be protected; copying a substantial part
can infringe even when the whole work is not reproduced. It also notes that
names and titles are not usually protected by copyright and that duration
depends on the kind and history of the material.

For the United States, the Copyright Office's
[game registration guidance](https://www.copyright.gov/register/tx-games.html)
and [Circular 33](https://www.copyright.gov/circs/circ33.pdf) distinguish an
idea, procedure, process, system or method of operation from the protectable
literary, graphic or artistic expression used to explain it. This is useful
guidance for a product that may circulate internationally, but it is not a
substitute for Australian analysis or advice about a particular dispute.

Branding is a separate issue. IP Australia explains that
[trade marks can protect](https://www.ipaustralia.gov.au/trade-marks/what-are-trade-marks)
names, words, phrases, logos and other signs that distinguish a product or
service. A mechanically independent product can still create a problem through
its name, cover, trade dress or marketing.

### What this means in practice

We may study general functions and independently implement common ideas such as
branching passages, health, skill selection, random checks, inventory and state
flags. We should not copy or closely paraphrase another system's:

- rule text, examples, flavour text or explanatory sequence;
- numerical tables or charts;
- distinctive character sheet or play-aid artwork;
- illustrations, maps, icons, typography or page composition;
- named attributes, spells, classes, Disciplines, special items or setting
  lore;
- selection and arrangement of rules where the same recognisable bundle is
  unnecessary;
- branded series terms, logos, slogans or presentation.

The distinction is not a licence to clone mechanics with synonyms. Independent
design quality demands more. If a reader can accurately describe the result as
“*Fighting Fantasy* with renamed stats” or “*Heart of Ice* with a different
skill list”, the design has failed this project's originality goal regardless
of the eventual legal conclusion.

### Public-domain source discipline

The underlying story and the edition used to obtain it are separate rights
questions. A public-domain original does not automatically free a later
translation, introduction, annotation, illustration, cover or typographical
edition. Rights status can also differ between countries.

For every source story, retain:

- author, title, first-publication details and date of death;
- source edition, scan or transcription provenance;
- the territory-specific basis for public-domain use;
- a record of editorial changes made during conversion;
- separate provenance for any illustrations, maps or paratext;
- a check that no proprietary adaptation supplied text or invented elements.

The project already records the initial story's provenance and preliminary
territorial analysis in
[`stories/public_domain/howard/tower_of_the_elephant/README.md`](../../stories/public_domain/howard/tower_of_the_elephant/README.md).
That assessment should be reviewed again before public or commercial release,
especially if the release territory changes.

### Independent-design record

Every material mechanic should eventually receive an entry like this:

| Field | Required record |
| --- | --- |
| Design need | The reader decision, uncertainty or consequence the rule must support |
| Parent-RPG source | The concept in Barry's RPG from which work began |
| Adaptation transformation | What was removed, combined or changed for authored solo play, and why |
| Story evidence | The recurring passages or pressures in the source that justify it |
| Closest comparators | Existing systems that perform a similar function |
| Material differences | Procedure, probability, state, reader decision and presentation differences |
| Original expression | New terminology, prose, examples, layout and play aid |
| Playtest evidence | What behaviour occurred and whether the rule earned its overhead |
| Decision | Retain, revise or remove, with date and rationale |

This provenance ledger is both a design tool and evidence of independent work.
It should capture rejected ideas as well as the final rules; a reconstructed
rationale written after the fact is less credible and less useful.

### Similarity audit before release

Once a candidate system exists, compare it at minimum with *Fighting Fantasy*,
*Lone Wolf*, Virtual Reality / *Heart of Ice*, ACE Gamebooks and the relevant
mechanics in Barry's full RPG.

For each comparator, examine:

1. attribute count, names, ranges and generation;
2. randomisation method and probability curve;
3. test and opposition procedures;
4. damage, recovery, failure and death;
5. combat sequence and reader decisions within it;
6. skills, powers and how they gate passages;
7. inventory limits and story-key use;
8. campaign advancement and carry-over;
9. state notation, adventure sheet and lookup tables;
10. order, wording and examples used to teach the rules;
11. visual identity, title and marketing claims;
12. the overall combination and resulting play experience.

A similarity should be classified as:

- **genre convention** — common and necessary to the form;
- **independently derived functional overlap** — similar purpose, materially
  different implementation with recorded rationale;
- **avoidable resemblance** — no strong reason to retain it; redesign;
- **potentially distinctive borrowing** — stop and obtain advice before use.

### Naming and release gates

Before choosing a public system or series name:

- search IP Australia's trade-mark database and relevant overseas databases;
- search booksellers, game databases, domains and social platforms for existing
  game uses;
- avoid names or taglines that imply endorsement by established series;
- commission or create independent logos, sheets and layouts;
- describe inspirations historically rather than using another brand as the
  product category.

Before publishing an adaptation:

- re-confirm story and edition rights in every intended territory;
- complete the mechanics provenance ledger and similarity audit;
- check all copied source passages against the verified public-domain text;
- verify provenance and licences for art, fonts and other assets;
- obtain legal review where similarity, branding or rights remain uncertain.

## Recommended comparative reading and playtesting

Rules summaries reveal procedures; they do not reveal fatigue, perceived
fairness, rereading cost or how the choices feel. The next research tranche
should be controlled play rather than another broad catalogue.

### Core comparison set

1. **One early *Fighting Fantasy* title**, ideally *The Warlock of Firetop
   Mountain*, to establish the foundational stat/combat/true-path experience.
2. **One more structurally ambitious *Fighting Fantasy* or *Sorcery!* volume**
   to separate limitations of the chassis from limitations of an early book.
3. ***Flight from the Dark*** through Project Aon's authorised edition, to test
   Discipline choice, the combat table and first-to-second-book carry-over.
4. ***Heart of Ice***, the key diceless capability-gating comparator.
5. ***Fabled Lands 1: The War-Torn Kingdom***, focusing on revisits, local
   versus global state and bookkeeping.
6. ***Buffalo Castle*** or another introductory *Tunnels & Trolls* solo, with
   the required RPG rules, to measure the cost of full-system compatibility.
7. **One ACE adaptation**, preferably *Beowulf Beastslayer* or *Dracula: Curse
   of the Vampire*, because it is the closest category precedent.
8. **One Choose Cthulhu volume**, to inspect a light, canonical-plus-alternative
   adaptation of a short story.

### Secondary comparison set

- *Way of the Tiger 1* for protagonist-specific tactical conflict;
- *Blood Sword 1* for solo/party role design;
- *DestinyQuest 1* for build, loot and quest-map structure;
- one ChoiceScript work and a small ink example for delayed consequence and
  stateful reconvergence;
- Advanced Fighting Fantasy's current quickstart or sample to identify what its
  tabletop expansion added to the gamebook chassis.

Use authorised digital editions, purchased books, library copies or legitimate
publisher samples. Do not build the research corpus from unauthorised scans.

### Common observation sheet

Each playthrough should record:

- initial character decisions and whether their consequences were intelligible;
- passages read, unique passages read and terminal outcome;
- choices with an informed basis versus guesses;
- checks rolled, their probabilities where known and their consequences;
- combat rounds, decisions made during combat and elapsed time;
- state marks, erasures and table lookups;
- unavailable options revealed by the text;
- reconvergences that did or did not remember prior choices;
- terminal failures and estimated rereading required;
- moments when mechanics reinforced or contradicted the fiction;
- desire to replay, and whether replay would involve new decisions or route
  memorisation.

Two playthroughs with contrasting legal builds are more informative than one
completion. For systems with random starting scores, replay the same route at a
low and high legal score or simulate the outcome distribution. The goal is to
measure play, not merely to finish the book.

## Questions to carry into system design

The research narrows the next interview, but does not answer it. The major
decisions, taken one at a time, are:

1. Which functions of the full RPG are essential to the experience Barry wants
   from a gamebook?
2. Is the reader playing Howard's Conan as a mechanically fixed character,
   choosing an interpretation of Conan, or creating a more general protagonist?
3. What should player choice decide directly, and what uncertainty should
   remain random?
4. What should a failed action do besides end play or subtract health?
5. How tightly should successful play converge on the canonical ending?
6. What is the maximum acceptable adventure-sheet and lookup burden?
7. Should the reusable layer have one universal resource model, or a stable
   resolution core with story-specific resources?
8. Is cross-story character persistence a real goal, or only reusable
   production infrastructure?

The highest-value next step is to answer the first question by mapping Barry's
full RPG subsystems to the six narrative functions in this document. After
that, *The Tower of the Elephant* can be annotated for invariants and decision
seams before any dice formula or character sheet is chosen.

## Limitations of this review

- This is a design-oriented survey, not an exhaustive academic history or a
  systematic review of every English- and non-English-language gamebook line.
- Many proprietary books were assessed from authorised samples, official
  rules, designer accounts and specialist bibliographic records rather than a
  fresh full playthrough.
- Individual titles often modify their series rules. A family-level summary
  should not be treated as an exact description of every volume or edition.
- Commercial availability, publisher ownership and living rule editions can
  change after the research date.
- The legal section describes conservative working practice. It is not a
  freedom-to-operate opinion, patent search, trade-mark clearance or advice on
  the final product.
- The proposed novelty territory remains a hypothesis until a candidate system
  exists and the closest comparators have been played and audited directly.

## Selected source index

### Official and authorised rules, histories and product records

- [Choose Your Own Adventure: official history](https://www.cyoa.com/our-history/)
- [Fighting Fantasy: Advanced Fighting Fantasy overview](https://www.fightingfantasy.com/advanced-fighting-fantasy-1)
- [Fighting Fantasy: *Sorcery!* overview](https://www.fightingfantasy.com/steve-jackson-s-sorcery)
- [Project Aon: Kai rules](https://www.projectaon.org/en/ReadersHandbook/Kai)
- [Project Aon: Kai Disciplines](https://www.projectaon.org/en/ReadersHandbook/KaiDisciplines)
- [Project Aon: Kai combat](https://www.projectaon.org/en/ReadersHandbook/KaiCombat)
- [ACE Gamebooks: series overview](https://www.acegamebooks.com/about-ace-gamebooks)
- [Choose Cthulhu: project and adaptation approach](https://choosecthulhu.es/en/what-is-choose-cthulhu/?v=da4b060a2e90)
- [DestinyQuest: official site](https://www.destiny-quest.com/)
- [DestinyQuest: official downloads](https://www.destiny-quest.com/downloads/)
- [ink: official site](https://www.inklestudios.com/ink/)
- [ink: writing manual](https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md)
- [Twine: official site](https://twinery.org/)

### Designer and publisher commentary

- [Dave Morris: Virtual Reality author guidelines](https://fabledlands.blogspot.com/2018/03/so-you-want-to-write-gamebook.html)
- [Dave Morris: local tickboxes, global codewords and passage logic](https://fabledlands.blogspot.com/2022/02/two-styles-of-gamebook-design.html)
- [Dave Morris: *Blood Sword* retrospective](https://fabledlands.blogspot.com/2014/08/blood-sword-redux-demons-claw.html)
- [Choice of Games: controlling branching with vignettes and variables](https://www.choiceofgames.com/2010/01/vignette-structure-as-a-means-of-controlling-branching/)
- [Choice of Games: principles for interesting choices](https://www.choiceofgames.com/2010/03/5-rules-for-writing-interesting-choices-in-multiple-choice-games/)
- [Michael J. Ward: *DestinyQuest* retrospective starting guide](https://www.destiny-quest.com/news/destinyquest-so-where-do-i-start/)

### Rules samples and specialist records

- [FightingFantasy.net: testing attributes and Luck](https://fightingfantasy.net/articles/creating-a-fighting-fantasy-adventure-step-by-step-part-3)
- [Gamebooks.org: *Fighting Fantasy*](https://www.gamebooks.org/Series/11/Show)
- [Gamebooks.org: *Tunnels & Trolls*](https://gamebooks.org/Series/111/Show)
- [Gamebooks.org: *Sorcery!* spellbook](https://www.gamebooks.org/Item/104/Editions)
- [Gamebooks.org: *Way of the Tiger*](https://www.gamebooks.org/Series/469/Show)
- [Gamebooks.org: *Blood Sword*](https://gamebooks.org/Series/56/Show)
- [Gamebooks.org: ACE Gamebooks](https://gamebooks.org/Series/1734/Show)
- [Gamebooks.org: *Dracula: Curse of the Vampire*](https://gamebooks.org/Item/12609/Show)
- [Gamebooks.org: Cretan Chronicles](https://gamebooks.org/Series/96/Show)
- [Gamebooks.org: Advanced Dungeons & Dragons Adventure Gamebooks](https://gamebooks.org/Series/21/Show)
- [Gamebooks.org: Middle-earth Quest](https://www.gamebooks.org/Series/270/Show)
- [Gamebooks.org: Sherlock Holmes Solo Mysteries](https://gamebooks.org/Series/389/Show)
- [Gamebooks.org: *Forbidden Gateway*](https://gamebooks.org/Series/173)
- [Gamebooks.org: *Falcon*](https://gamebooks.org/Series/146/Show)
- [Gamebooks.org: *Time Machine*](https://gamebooks.org/Series/78/Show)
- [Gamebooks.org: *GrailQuest*](https://gamebooks.org/Series/188/Show)
- [Gamebooks.org: *Be an Interplanetary Spy*](https://gamebooks.org/Series/6/Show)
- [Gamebooks.org: 1 on 1 Adventure Gamebooks](https://gamebooks.org/Series/291/Show)
- [Gamebooks.org: *Ace of Aces*](https://gamebooks.org/Series/18/Show)
- [Gamebooks.org: *Lost Worlds*](https://gamebooks.org/Series/49/Show)
- [Gamebooks.org: *Legendary Kingdoms*](https://gamebooks.org/Series/2125/Show)
- [Virtual Reality / *Heart of Ice* sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/478171-sample.pdf)
- [*Fabled Lands 1* sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/528417-sample.pdf)
- [*Way of the Tiger* sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/527552-sample.pdf)
- [*Blood Sword* sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/478195-sample.pdf)
- [Advanced Fighting Fantasy second-edition sample](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/453554-sample.pdf)
- [Christian Swinehart: structural visualisations of choice books](https://samizdat.co/cyoa/)
- [Iain Johnston: mathematical analysis of *Fighting Fantasy* Luck](https://arxiv.org/abs/2002.10172)

### Intellectual-property guidance

- [Australian Attorney-General's Department: copyright basics](https://www.ag.gov.au/rights-and-protections/copyright/copyright-basics)
- [U.S. Copyright Office: games](https://www.copyright.gov/register/tx-games.html)
- [U.S. Copyright Office: Circular 33, *Works Not Protected by Copyright*](https://www.copyright.gov/circs/circ33.pdf)
- [IP Australia: what trade marks protect](https://www.ipaustralia.gov.au/trade-marks/what-are-trade-marks)

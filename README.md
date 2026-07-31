# Gamebook

A project to develop a streamlined gamebook system based on a cut-down version
of Barry W. Brook's full RPG ruleset.

The first adaptation and playtest will use Robert E. Howard's *The Tower of the
Elephant*. The longer-term aim is an expandable system for turning suitable
public-domain fiction into gamebooks, while also supporting original stories.

## Status

The approved
[Authored S&S solo core](docs/superpowers/specs/2026-07-30-authored-sinew-steel-solo-core-design.md)
now has a
[*Tower of the Elephant* adaptation map](stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md)
and a
[paper-playable outer-wall slice](stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md).
The passage schema, deterministic tooling, and AI facilitation remain later
increments.

## Background research

- [Gamebook systems: background research and design guardrails](docs/research/gamebook-systems-background.md)
  surveys major gamebook approaches, branching and state techniques, recurrent
  failure modes, public-domain adaptation precedents, and originality/IP
  guardrails for the eventual system.

## Story workspaces

- `stories/public_domain/howard/tower_of_the_elephant/` — first adaptation and
  playtest.
- `stories/original/` — reserved for possible original works.

The Tower workspace records source provenance, conversion, and the applicable
rights basis alongside its adaptation work.

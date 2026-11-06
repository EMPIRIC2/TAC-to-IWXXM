# Clarity: no project jargon, no ambiguous reference

These rules extend ASD-STE100 for this repository. Every Markdown document must
stand alone. A reader who does not know the project must understand each sentence
on first read. Nothing important may depend on unspoken team context.

## Stand-alone explanation

1. **Explain from the start.** The first time a domain, product, package, UI, or
   process name appears in a document, give a short plain definition in the same
   sentence or the next sentence (one concept per sentence).
2. **No unexplained jargon.** Do not leave project shorthand, nicknames, or
   insider labels in editable prose unless you define them immediately.
3. **Prefer full names over private codes.** In prose, do not rely on session,
   evolve, feature, or ticket shorthand alone (`EV-048`, `S057`, `F16`, `#951`)
   as if the reader already knows them. If a tracking id must appear, put the
   plain-language name first, then the id in parentheses, or keep the id only in
   a protected `[Corpus: …]` cite / code / table column the skill must not rewrite.
4. **Acronyms:** write the full form, then the acronym in parentheses, at first
   use in that file. After that, the acronym alone is allowed in the same file
   only when the referent stays obvious.
5. **Package and path names in prose:** say what the thing does, then give the
   path or package id in backticks if needed.
   - Weak: `` `tac-decoding` handles NL. ``
   - Clear: `The tac-decoding package turns Traditional Alphanumeric Code (TAC) into a plain-language summary.`

## No ambiguous reference (track every noun)

Every determiner and pronoun must point to one noun the reader can name without
guessing. If the reader cannot answer “which exact thing?”, rewrite.

| Pattern | Problem | Fix |
|---------|---------|-----|
| `this` / `that` / `these` / `those` with no noun | Referent unclear | Repeat the noun: `this warning`, `that schema pin` |
| `it` / `they` / `them` with two possible nouns | Ambiguous | Repeat the noun |
| `the` + vague noun (`the process`, `the service`, `the issue`, `the change`) | Many possible referents | Name the process, service, issue, or change |
| `the above` / `the following` / `as mentioned` | Forces the reader to search | Name the section, heading, or step |
| `here` / `there` / `this way` for locations or methods | Not trackable | Name the path, URL, host, or method |
| `we` / `our` for an unnamed team or system | Actor unclear | Name the component or the operator role |
| `etc.` / `and so on` / `and more` | Open-ended set | List the items, or stop after the last real item |

**Articles stay.** ASD-STE100 Rule 4.5 still requires `a` / `an` / `the` where
grammar needs them. Do not delete articles to sound “plain.” Make the noun after
the article specific enough to track.

**`that` as a conjunction stays when it removes ambiguity** (GR-1), for example
`Make sure that the valve is open.` Do not confuse connector `that` with
demonstrative `that` used as a vague pointer.

### Test (required)

For every `the`, `this`, `that`, `it`, `they`, and `them` in editable prose, ask:

> Can the reader point to one concrete noun, path, UI label, or prior defined
> term without project knowledge?

If no → finding `[Clarity:ambiguous-ref]`. In rewrite mode, replace with the
explicit noun phrase.

## Ban list for unexplained project talk

Treat these as jargon until defined in the same document (not exhaustive):

- Internal UI nicknames without the on-screen label
- Pipeline stage slang (“the cutover”, “the soft-fail path”) with no procedure name
- Env var names in prose without saying what they control
- “Prod”, “stage”, “main” as places without saying they are Git branches or deploy
  environments
- Homegrown verbs (`pin`, `disseminate`, `quarantine`) used as if everyday English
  when the project meaning differs — define the project meaning first

Protected code, commands, and identifiers may still use the short form. Surrounding
prose must carry the explanation.

## Check report tags

| Tag | Use |
|-----|-----|
| `[Clarity:jargon]` | Project or domain term used without a stand-alone explanation |
| `[Clarity:ambiguous-ref]` | Determiner/pronoun/noun phrase with no unique trackable referent |
| `[Clarity:assumed-context]` | Sentence only makes sense if the reader already knows the repo |

Always pair the tag with a rewritten sentence that a new reader can follow.

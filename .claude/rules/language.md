# Language — the system writes English; campaigns speak the community's language

Every author-controlled string in this repo is **English**. The only surface
that legitimately switches language is the **campaign output** — a community
in Guadalajara gets outreach copy in Spanish; a community in Portland gets
English. The chrome, prompts, schemas, comments and commits stay English.

## IN scope (must be English)

| Surface | Why |
|---|---|
| UI copy (labels, placeholders, aria-labels, errors, empty states) | judges + contributors read English |
| Agent role prompts (`agents/*/SPEC.md` and runtime prompts) | the SDK/models work best in English; output language is a VOICE instruction, not a prompt language |
| Schema titles/descriptions (`contracts/*.schema.json`) | contracts are documentation |
| Code comments, commit messages, PR titles | reviewers don't bounce off a language wall |
| README, docs, submission assets | the jury reads English |

## OUT of scope (the product's multilingual surface)

- **Campaign artifacts** (outreach copy, flyer text, task descriptions):
  match the language of the community/concern. This is a VOICE rule inside
  the OUTREACH/COORDINATOR prompts — "write deliverables in the language of
  the submitted concern".
- **Fetched evidence**: whatever the source says is whatever it says.

## Applying it

1. New string in UI/prompt/schema? English. If the thought arrived in
   Spanish, translate before committing.
2. Found Spanish in a file you're editing? Migrate it in the same PR
   (boy-scout rule).
3. Demo seed concern may be Spanish-language (greenwashing case in MX) —
   that's the multilingual surface working, not a violation. The chrome
   around it stays English.

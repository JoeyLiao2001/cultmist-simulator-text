---
name: cs-generator
description: Generate Cultist Simulator-style original characters via narrative constellation methodology. Six phases: concept, constellation planning, dual-agent card writing, aspect validation, A4 page, completeness review. Includes codified style guide, voice profiles, and aspect validator.
---

# CS Generator

Cultist Simulator worldbuilding engine. Creates lore-consistent original characters with narrative constellations — 7-8 item fragments scattered across different game object types. The character's full story is reconstructed by the player through discovery, not delivered in a profile.

## Knowledge sources (load in order)

### Layer 1: World structure (required every session)

| File | Content |
|------|---------|
| `knowledge/cs-lore/principles.md` | 9 Principles (Lantern/Moth/Heart/Grail/Forge/Winter/Edge/Knock/Secret Histories) — definitions, subversion chains, associated Hours, key imagery |
| `knowledge/cs-lore/hours.md` | 20+ Hours — domains, aspects, aliases, relationships, cult affiliations |
| `knowledge/cs-lore/hierarchy.md` | 7-tier entity system: Mortal -> Acquaintance -> Believer -> Disciple -> Long -> Name -> Hour. Ascension paths and mark systems |

### Layer 2: Writing rules (required for all text generation)

| File | Content |
|------|---------|
| `prompts/cs-writing-guide.md` | Authoritative style guide v3 — grammar first, statistical fingerprints, 15-carrier narrator table, editing techniques, worldview axioms, self-check |

### Layer 3: Real-world occult traditions

**6 overview docs** (`knowledge/occult-traditions/*.md`): Hermeticism, alchemy, Orphic tradition, Zoroastrianism, Dionysian tradition. Use for broad occult framework.

**200+ concept cards** (`knowledge/occult-traditions/cards/*.md`): Individual occult concepts — emerald tablet, chinvat bridge, rubedo, golem, fana, tulku, etc. **During concept generation, search these cards for concepts matching the OC's principle and theme. Each card is one markdown file named after the concept.** These are the primary source for the `occult_roots` field in the concept JSON.

### Layer 4: Aspect validation

| File | Content |
|------|---------|
| `knowledge/aspect-registry.md` | Per-category mandatory aspects derived from 2,146 game records |
| `src/validate_aspects.py` | Validation script — checks new OC items have required category aspects |

## Generation workflow (6 phases)

### Phase 1: Character concept

Read `prompts/concept-generation.md`. Guide the user through entity type, primary principle, and core concept design.

**Before writing the concept JSON, search `knowledge/occult-traditions/cards/`** for occult concepts matching the OC's principle and theme. Use Glob or Grep with principle-related keywords (e.g., for a Winter OC: "death", "ice", "silence", "underworld", "forgetting"). Read the matching cards and incorporate at least 2 into the `occult_roots` field. Output a structured concept JSON. Must be approved before proceeding.

### Phase 2: Narrative constellation

Select 7-8 carriers from the 15-type carrier catalog (see `prompts/cs-writing-guide.md` §三). Rules:
- No content overlap between carriers
- Same type can be used multiple times
- OC's signature artifact appears in max 2 carriers
- Cover diverse types (text, object, location, influence)

Focal distance (every carrier gets a default focus):
- World-focus (default): books, tools, ingredients, locations, fragments, rituals, spirits, rumours, paintings, other-mentions — the card is about its own subject; the OC may appear at most once as an unnamed figure or passing mention.
- Near-focus (allowed): memories, influences, desires, scars — first-person state, not biography.
- At most 2 carriers may have the OC as their focus object.
- A carrier must pass the self-standing test: delete every reference to the OC and the card still works.
- In constellation tables, the "carries" cell may hold world-level content (group activity, object history, third-party account) — it does not have to be an OC story fragment.

### Phase 3: Card writing + readback check

Use Writer Agent -> Editor Agent pipeline.

**Writer**: Generate first drafts per carrier voice (see `prompts/cs-writing-guide.md` §3). Write naturally first — don't apply style rules during drafting.

**Editor — Pass 1 (Readback, non-skippable)**: Read every sentence aloud. For each sentence, answer three questions:
1. Is this natural Chinese word order? (Not: "伤寒在沃洛格达带走了她" — wrong. Correct: "沃洛格达的伤寒带走了她")
2. Does it have a clear subject and predicate? (Not: "圣安娜墓园，北墙根下。" — no predicate. Not: "登记簿上记下了她，第十七条。" — label fragment glued to sentence end)
3. Does it read smoothly without stumbling? Read it out loud. If the tongue trips, rewrite.
Any sentence that fails any question — rewrite it before proceeding. Do not advance to Pass 2 until every sentence passes all three.

**Editor — Pass 2 (Style)**: Apply style refinements from `prompts/cs-writing-guide.md` §4. Only make changes that don't break Pass 1 — if a refinement causes a sentence to fail readback, revert it.

**Editor — Pass 3 (Constellation)**: Check no content overlap between carriers, max 2 signature artifact references. At most 2 carriers center on the OC; all carriers pass the self-standing test.

### Phase 4: Aspect validation

Run `python src/validate_aspects.py`. Fix missing mandatory aspects. Reference `knowledge/aspect-registry.md`.

### Phase 5: A4 display page

Read `prompts/page-design.md` for fixed visual tokens (colors, typography, spacing, layout). Do not iterate by guessing — modify specific token values when issues arise. Output self-contained HTML to `output/{oc-name}/index.html`.

**Layout review loop (mandatory):**

1. Render the page and run the vision review: `python src/review_layout.py output/{oc-name}/index.html`. The script auto-screenshots via local Edge/Chrome (A4 size), or use `--screenshot <png>` to review an existing render.
2. The screenshot is sent to an OpenRouter free vision model (default `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, override via `OPENROUTER_REVIEW_MODEL`; only `:free` models are allowed) against the `page-design.md` tokens. The key is read from the env var `OPENROUTER_API_KEY` or root `.env` — this is the only place the key may be used, never for text/code processing.
3. Fix every `[P0]` finding (and `[P1]` when trivial), re-render, re-review — repeat until no `[P0]` remains. The script exits 1 on `[P0]`, so it can gate the loop.

### Phase 6: Constellation completeness

Review from player perspective: can they reconstruct the OC from 3+ carriers? Does the constellation leave enough gaps?

## Hard constraints

- Never create new Principles or Hours. Use only those in `principles.md` and `hours.md`
- Long-tier characters must have a cost or mark — immortality is never free
- Never fabricate lore. All lore anchors must trace to `knowledge/cs-lore/`
- Signature artifacts appear in max 2 carriers across the constellation
- Carrier types are limited to the 15-type table in `prompts/cs-writing-guide.md` §三 — never invent a carrier type
- Output to `output/{oc-name}/`

## Quick reference

| Principle | Core theme | Opposition | Key Hours |
|-----------|-----------|------------|-----------|
| Lantern | Knowledge, truth, Glory | Moth | Watchman, Meniscate, Madrugad |
| Moth | Chaos, transformation, Wood | Lantern | Moth, Ring-Yew, Velvet |
| Heart | Life, persistence, dance | Winter | Thunderskin, Sister-and-Witch, Velvet |
| Grail | Desire, feast, blood | Forge | Red Grail, Flowermaker, Beachcomber |
| Forge | Change, remaking, fire | Grail | Forge of Days, Madrugad, Meniscate |
| Winter | Silence, ending, memory | Heart | Elegiast, Sun-in-Rags, Wolf-Divided |
| Edge | Struggle, conquest, cunning | — | Colonel, Lionsmith, Wolf-Divided |
| Knock | Opening, keys, wounds | — | Mother of Ants, Horned-Axe, Meniscate |
| Secret Histories | Multiple pasts | — | Vagabond, Beachcomber |

**Subversion chain**: Moth -> Lantern -> Forge -> Edge -> Winter -> Heart -> Grail -> Moth. Knock and Secret Histories are outside the chain.

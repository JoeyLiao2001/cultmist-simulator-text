---
name: cs-generator
description: Generate Cultist Simulator-style original characters and narrative constellations. 6-phase pipeline: concept -> constellation -> dual-agent card writing -> aspect validation -> A4 page -> completeness review. Includes a codified style guide with 10 writing rules, 18 carrier-type voice profiles, and an aspect registry with validator.
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
| `prompts/cs-writing-guide.md` | Complete style guide — Rule 0 (grammar first), 10 writing rules, 18 carrier-type voice profiles, 7-dimension framework, 9 editing techniques |

### Layer 3: Real-world occult traditions

| File | Content |
|------|---------|
| `knowledge/occult-traditions/` | Hermeticism, alchemy, Orphic tradition, Zoroastrianism, Dionysian tradition. Use for occult root references |

### Layer 4: Aspect validation

| File | Content |
|------|---------|
| `knowledge/aspect-registry.md` | Per-category mandatory aspects derived from 2,146 game records |
| `src/validate_aspects.py` | Validation script — checks new OC items have required category aspects |

## Generation workflow (6 phases)

### Phase 1: Character concept

Read `prompts/concept-generation.md`. Guide the user through entity type, primary principle, and core concept design. Output a structured concept JSON. Must be approved before proceeding.

### Phase 2: Narrative constellation

Select 7-8 carriers from the 28-type catalog (see writing guide). Rules:
- No content overlap between carriers
- Same type can be used multiple times
- OC's signature artifact appears in max 2 carriers
- Cover diverse types (text, object, location, influence)

### Phase 3: Dual-agent card writing

Use Writer Agent -> Editor Agent pipeline. The Writer generates first drafts per carrier voice. The Editor performs 3-pass review:
1. Grammar (Rule 0 — sentence readability)
2. Style (10 writing rules, voice profiles, banned patterns)
3. Constellation consistency (no content overlap, max 2 signature artifact references)

### Phase 4: Aspect validation

Run `python src/validate_aspects.py`. Fix missing mandatory aspects. Reference `knowledge/aspect-registry.md`.

### Phase 5: A4 display page

Read `prompts/page-design.md` for fixed visual tokens (colors, typography, spacing, layout). Do not iterate by guessing — modify specific token values when issues arise. Output self-contained HTML to `output/{oc-name}/index.html`.

### Phase 6: Constellation completeness

Review from player perspective: can they reconstruct the OC from 3+ carriers? Does the constellation leave enough gaps?

## Hard constraints

- Never create new Principles or Hours. Use only those in `principles.md` and `hours.md`
- Long-tier characters must have a cost or mark — immortality is never free
- Never fabricate lore. All lore anchors must trace to `knowledge/cs-lore/`
- Signature artifacts appear in max 2 carriers across the constellation
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

# V2 Design Plan — Neural Memory App (debug-test-001)

## Phase 1: Competitive Analysis ✅
**Status:** Complete

### Top 5 Competitors Evaluated

| Competitor | Local-first | Graph Viz | API | No API Key | Open Source |
|---|---|---|---|---|---|
| **Obsidian** | ✅ Local vault | ✅ Built-in | ⚠️ Plugin API | ✅ | ⚠️ Proprietary |
| **Logseq** | ✅ Local files | ✅ Built-in | ⚠️ Plugin API | ✅ | ⚠️ AGPL (free tier) |
| **Cognee** | ⚠️ Docker compose | ⚠️ API only | ✅ 4-verb | ⚠️ Needs LLM key | ✅ Apache 2.0 |
| **Mem0** | ⚠️ Optional | ⚠️ Limited | ✅ SDK | ⚠️ Needs LLM key | ✅ Apache 2.0 |
| **Zep/Graphiti** | ⚠️ Neo4j server | ⚠️ API only | ✅ | ⚠️ Needs LLM key | ✅ MIT |

### Key Finding
Our unique position: **single Python file + zero external services + full D3 graph + REST API**
that runs with no DB server, no Docker, no API key. Competitors trade portability for features.

## Phase 2: DESIGN.md ✅
**Status:** Complete

- `DESIGN.md` — Google spec compliant (0 lint errors via `@google/design.md`)
- `tailwind.theme.json` — Tailwind v3 theme export generated
- `tokens.json` — W3C DTCG format export generated
- WCAG contrast validated: all components ≥ AA

### Token Summary
- 30 colors (dark theme palette + 16 category-specific graph node colors)
- 7 typography scales (heading, subheading, body-lg/md/sm, mono, label)
- 4 rounding levels (sm=4px, md=8px, lg=12px, full)
- 5 spacing tokens (xs=4px through xl=32px)
- 10 component specs (buttons, cards, inputs, stat boxes, legend dots)

### V2 Roadmap (4 Tiers)
| Tier | Features | Status |
|------|----------|--------|
| Tier 1 | Semantic search (cosine similarity), relationship management UI | TODO |
| Tier 2 | Dark/light theme toggle, graph export (PNG/SVG) | TODO |
| Tier 3 | Fact linking UI (drag to create relationships), multi-project | TODO |
| Tier 4 | Analytics dashboard, temporal memory views | TODO |

## Phase 3: HTML Blueprint ✅
**Status:** Complete

- `blueprint_v2.html` — 43KB interactive prototype
- **Monitor surface** archetype: density + glanceable hierarchy (no hero+3 cards)
- D3.js v7 force-directed graph with category-colored nodes (10 categories)
- Semantic search input with live filtering on facts list
- CRUD fact manager: create/edit/delete with form validation
- Dark/light theme toggle with CSS variables
- Node detail modal with connection traversal
- Graph search highlighting + legend with category colors
- All DESIGN.md tokens mapped to `:root` CSS variables
- Slop self-audit: 0/10 (clean — no tech gradients, no unearned blur, no hero+3 cards)

## Phase 4: TDD Build — Next
**Status:** Pending

Following `design-led-tdd-workflow`:

### Tier 1: Semantic Search (cosine similarity on embeddings)
- RED test: `/api/search?q=memory&semantic=true` returns facts with similarity scores
- GREEN: Add cosine similarity computation using stored embeddings
- Test: `python test_api.py` must still pass all existing tests (80/80)

### Tier 1: Relationship Management UI
- RED test: POST to `/api/facts` with `method: LINK` creates relationship
- GREEN: Add LINK method handler in server.py + UI button in blueprint
- Test: Relationship appears in graph endpoint

### Future Tiers (Phase 5-7)
- Tier 2: Theme toggle endpoint, graph export (PNG/SVG)
- Tier 3: Drag-to-link graph nodes, multi-project tags
- Tier 4: Analytics dashboard, temporal memory views

---

*Plan created: 2026-09-27*
*Branch: v2design*
*Commit: 3af9add (DESIGN.md + token exports)*

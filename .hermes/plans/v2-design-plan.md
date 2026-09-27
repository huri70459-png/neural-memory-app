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

## Phase 3: HTML Blueprint Prototype — Next
**Status:** Pending

Use `claude-design` skill to create an interactive HTML blueprint for the V2 UI:
- Monitor surface archetype (density + glanceable hierarchy)
- D3 force graph with category-colored nodes
- Semantic search input with results highlighting
- CRUD fact manager with form validation
- Dark theme matching DESIGN.md tokens

## Phase 4: TDD Build — Pending
Following `design-led-tdd-workflow`:
1. Write DESIGN.md blueprint features as test cases
2. RED → GREEN → COMMIT for each Tier 1 feature
3. Regression test after each tier

---

*Plan created: 2026-09-27*
*Branch: v2design*
*Commit: 3af9add (DESIGN.md + token exports)*
